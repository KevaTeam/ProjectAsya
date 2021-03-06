/**
 * Created by Дмитрий Муковкин on 22.11.2014.
 */

$(function() {
    var App = {
        config: {
            urlAPI: "/api/method/",
            client_id: 'web'
        },
        cache: {
            views: {}
        },
        Views: {},
        Models: {},
        Collections: {},
        Events: {},
        VK: 0
    };

    _.extend(App.Events, Backbone.Events);

    App.Views.Wrapper = Backbone.View.extend({
        el: $('#wrapper'),

        render: function(html) {
            this.$el.html(html);
        }
    });

    function clearCookie() {
        $.cookie('token', '');
        $.cookie('user_id', '');
        $.cookie('isAdmin', '');
    }
    
    function isUserLogin() {
        return !!$.cookie('token') && !!$.cookie('user_id');
    }

    App.Router = Backbone.Router.extend({
        routes: {
            '':       'timer',
            'login':  'login',
            'timer':  'timer',
            'tasks':  'tasks',
            'logout': 'logout',
            'end':    'end'
        },

        initialize: function() {
            App.Views.Main = new App.Views.Wrapper();
            console.log('Router initialize');
            Backbone.history.start();
        },

        execute: function (callback, args, name) {
            console.info('Working route %s', name);

            // Проверим вошел ли пользователь
            if (!isUserLogin() && name !== 'login') {
                console.warn('User is not log in');
                this.login();
                return;
            }

            if (callback) callback.apply(this, args);
        },

        login: function() {
            clearCookie();
            new App.Views.Login();
        },

        tasks: function () {
            var timer = App.cache.views.timer;
            if (!timer || timer.gameIsWaiting()) {
                console.log('Redirect to timer');
                Backbone.history.navigate('timer', { trigger: true });
                return true;
            }

            if (timer.gameIsEnded()) {
                console.log('The game is ended - redirect');
                Backbone.history.navigate('end', { trigger: true });
                return true;
            }

            console.log('Router: tasks');
            if (timer.gameIsRunning()) {
                new App.Views.Tasks();
            }
        },

        timer: function () {
            console.log('Router: timer');
            if(App.cache.views.timer === undefined) {
                App.cache.views.timer = new App.Views.Timer();
            }
            else {
                App.cache.views.timer.init();
            }
        },

        end: function() {
            App.cache.views.end = App.cache.views.end || new App.Views.End();
        },

        logout: function() {
            clearCookie();

            Backbone.history.navigate('login', {trigger: true});
        }

    });


    Backbone.sync = function(method, model, options) {
        //console.log(method, model, options);
        var params = {
            url: App.config.urlAPI + model.url,
            type: 'GET',
            dataType: 'json'
        };

        params.data = options.params || {};

        if ($.cookie('user_id')) {
            params.data.access_token = $.cookie('token');
        }

        var success = options.success;
        options.success = function (resp) {
            if (resp.error) {
                resp = resp.error;

                if(resp.description == "You are not logged") {
                    Backbone.history.navigate('login', {trigger: true});
                }

                var code = {
                    message: resp.description
                };

                model.trigger('error', code, xhr, options);

                return false;
            }
            model.trigger('before:add', model, resp.response, options);

            success(resp.response);

            model.trigger('sync', model, resp, options);
            //model.trigger('add', model, resp.response, options);
        };


        var xhr = options.xhr = Backbone.ajax(_.extend(params, options));

        model.trigger('request', model, xhr, options);
        return xhr;
    };


    App.Views.Timer = Backbone.View.extend({
        id: 'timer',

        initialize: function () {
            // Добавляем обработчик на событие начала игры
            App.Events.on("game:start", this.startEndTimer, this);

            this.init();
        },

        gameIsRunning: function () {
            return this.time.get('start') === 0 && this.time.get('end') > 0;
        },

        gameIsEnded: function () {
            return this.time.get('end') === 0;
        },

        gameIsWaiting: function () {
            return this.time.get('start') > 0;
        },

        timer: {
            seconds: '',
            minutes: '',
            hours: ''
        },

        init: function () {

            var Timer = new App.Models.Timer();

            this.listenTo(Timer, "change", this.setTime);

            // Render template
            this.listenToOnce(this, 'render', this.renderOnce);

            Timer.fetch();

            this.render()
        },

        renderOnce: function() {
            this.$el.html(new EJS({url: '/static/templates/timer/Timer.ejs'}).render());
            if ($.cookie('isAdmin')) {
                this.$el.find('.admin_button').show();
            }
        },

        render: function() {
            App.Views.Main.render(this.$el);
        },

        setTime: function(time) {
            console.log('Timer: set time');
            console.log(this, time);
            this.time = time;

            this.trigger('render');

            var timestamp = time.get('start');

            // Проверка на начало игры
            if (timestamp == 0) {
                App.Events.trigger('start_game');
                return false;
            }

            // Включаем обратный таймер
            this.updateTime(timestamp, $('#timerStart'));

            // А теперь обновляем время
            var self = this;

            App.cache['timerStart'] = setInterval(function () {
                timestamp --;
                if (timestamp == 0) {
                    App.Events.trigger('start_game');
                    return false;
                }

                self.updateTime(timestamp, $('#timerStart'));
            }, 1000);
        },

        startEndTimer: function() {
            App.cache['timerTimestamp'] = this.time.get('end');

            var self = this;
            console.log(App.cache['timerTimestamp']);
            if(App.cache['timerTimestamp'] > 0) {
                // Запускаем игру

                Backbone.history.navigate('tasks', {trigger: true});

                App.cache['timerEnd'] = setInterval(function () {
                    App.cache['timerTimestamp'] --;

                    self.updateTime(App.cache['timerTimestamp'], $('#timer'));

                    // Делаем таймер тру
                    if(App.cache['timerTimestamp'] < 3600) {
                        $('.hours, .text-hours').hide();
                    }
                    if(App.cache['timerTimestamp'] < 60) {
                        $('.minutes, .text-minutes').hide();
                        $('.seconds, .text-seconds').show();
                    }
                    if(App.cache['timerTimestamp'] <= 0)
                        App.Events.trigger('end_game');

                }, 1000);
            }
            else { // Игра уже закончилась
                console.log('stop game');
                App.Events.trigger('end_game');
            }
        },

        updateTime: function(timestamp, node) {
            App.cache['hours'] = Math.floor(timestamp / 3600);
            App.cache['minutes'] = Math.floor((timestamp - (App.cache['hours'] * 3600)) / 60);
            App.cache['seconds'] = timestamp - (App.cache['hours'] * 3600) - (App.cache['minutes'] * 60);

            $(node).find('.seconds').text(App.cache['seconds']);
            $(node).find('.text-seconds').text(rulesDeclination(App.cache['seconds'], ['секунда','секунды','секунд']));

            $(node).find('.minutes').text(App.cache['minutes']);
            $(node).find('.text-minutes').text(rulesDeclination(App.cache['minutes'], ['минута','минуты','минут']));

            $(node).find('.hours').text(App.cache['hours']);
            $(node).find('.text-hours').text(rulesDeclination(App.cache['hours'], ['час','часа','часов']));
        }
    });

    App.Views.End = Backbone.View.extend({
        el: $('#wrapper'),
        initialize: function() {
            this.render();
        },

        render: function() {
            this.$el.html(new EJS({url: '/static/templates/end/Main.ejs'}).render());
        }
    });

    App.Models.Timer = Backbone.Model.extend(   {
        url: 'timer.get',
        default_time: {
            start: 0,
            end: 3600
        },
        parse: function(response) {
            var start = 0,
                end = 3600;

            if (response.start && response.end) {
                start = response.start.delta;
                end = response.end.delta;
            }

            return {
                'start': start,
                'end': end
            };
        }
    });

    App.Views.Tasks = Backbone.View.extend({
        id: "tasks",

        initialize: function() {
            console.log('Initialize tasks');
            this.render();
            new App.Views.UserList({ el: this.$el.find('#users') });

            new App.Views.QuestList({ el: this.$el.find('#quest') });

            App.Views.Main.render(this.$el);
        },
        render: function() {
            this.$el.html(new EJS({url: '/static/templates/quest/Wrapper.ejs'}).render());
            return this;
        }
    });

    var QuestCategory = Backbone.Model.extend({
        parse: function (response) {
            return response;
        }
    });

    App.Collections.QuestList = Backbone.Collection.extend({
        model: QuestCategory,
        url: 'quest.list',
        initialize: function() {
            this.on('error', this.error, this);
        },
        error: function() {
            Backbone.history.navigate('login', {trigger: true});
        },
        parse: function(response) {
            App.cache['quests'] = response.items;
            return _.groupBy(response.items, function(obj) { return obj.section.id; });
        }
    });

    App.Views.QuestList = Backbone.View.extend({
        initialize: function() {
            this.collection = new App.Collections.QuestList();

            this.listenTo(this.collection, "add", this.render);

            Backbone.Events.on('quest:update', this.update, this);

            this.update();
        },
        events: {
            'click a.quest_title': "openModal"
        },

        update: function() {
            this.collection.fetch();
        },

        openModal: function (e) {
            var quest = _.find(App.cache['quests'], function(num){ return num.id == e.target.id; });

            (new App.Models.QuestTake).fetch({ params: { id: quest.id }});
            App.Views.Main.$el.find('.quest-modal .modal-content').html((new Task).render(quest).$el);
        },
        render: function (array) {
            // Sort by rating
            array.attributes = _.map(array.attributes, function(section) {
                return _.sortBy(section, function(item) { return item.score; });
            });
            // Список категорий в квестах
            sections = _.map(array.attributes, function(num, key){ return { id: key, title: num[0].section.title }} );
            this.$el.html(new EJS({url: '/static/templates/quest/QuestList.ejs'}).render({ sections: sections, arr: array.attributes }));

            return this;
        }

    });

    var Task = Backbone.View.extend({
        events: {
            'click button.answer': 'checkAnswer'
        },
        checkAnswer: function(e) {
            this.$el.find('.alert').hide();
            var Pass = new App.Models.QuestPass();
            Pass.fetch({params: {id: this.quest.id, answer: this.$el.find('#answer').val() }});
        },
        render: function(quest) {
            this.quest = quest;
            this.$el.html(new EJS({url: '/static/templates/quest/Modal.ejs'}).render(quest));
            return this;
        }
    });

    App.Models.QuestTake = Backbone.Model.extend({
        url: 'quest.take',
        parse: function(response) {
            console.log(response);
        }
    });

    App.Models.QuestPass = Backbone.Model.extend({
        url: 'quest.pass',
        initialize: function() {
            this.listenTo(this, 'error', this.showError);
        },

        showError: function(model) {
            var message = '';
            if(typeof model.message == 'object') {
                for (var item in model.message) {
                    for(var i in model.message[item]) {
                        message += model.message[item][i] + '\n';
                    }
                }
                $('.modal .alert-danger').text(message).show();
            }
            else
                $('.modal .alert-danger').text(model.message).show();
        },

        parse: function (response) {
            // Answer is not correct
            if (!response) {
                $('.modal .alert-danger').text('Ответ неверен').show();
                return true;
            }

            $('.modal .alert-success').show();

            Backbone.Events.trigger('quest:update');

            Backbone.Events.trigger('users:update');
        }
    });

    // Список пользователей

    App.Models.User = Backbone.Model.extend({
        parse: function(response) {
            return response
        }
    });

    App.Collections.Users = Backbone.Collection.extend({
        model: App.Models.User,
        url: 'rating.list',
        parse: function(response) {
            return {
                response: response.items
            };
        }
    });

    App.Views.UserList = Backbone.View.extend({
        events: {
            'click .admin': 'admin',
            'click .logout': 'logout',
            'click .news': 'news',
            'click .rating': 'rating'
        },

        initialize: function() {
            this.collection = new App.Collections.Users();

            this.listenTo(this.collection, "add", this.render);
            Backbone.Events.on('users:update', this.update, this);

            this.update();
        },

        admin: function () {
            window.location.href = '/admin';
        },

        logout: function() {
            console.log('logout');
            Backbone.history.navigate('logout', {trigger: true});
        },

        news: function() {
            this.$el.find('.block').hide();
            this.$el.find('.block-news').show();
        },

        rating: function () {
            this.$el.find('.block').hide();
            this.$el.find('.block-rating').show();
        },

        update: function() {
            this.collection.fetch({ params: { order: 'rating' }});
        },

        updateNews: function () {
            this.$el.find('#vk_groups').html('В разработке.')
        },

        render: function (array) {
            this.$el.html(new EJS({url: '/static/templates/quest/UserList.ejs'}).render({
                myRole: App.cache.role,
                user: array.attributes.response
            }));

            if (!$.cookie('isAdmin')) {
                this.$el.find('.admin').hide();
            }

            this.updateNews();
            var self = this;

            return this;
        }

    });

    // Конец списка пользователей

    App.Models.Auth = Backbone.Model.extend({
        initialize: function () {
            this.on('sync', this.setCookie, this);
            this.on('error', this.error, this);
        },

        url: '../token',

        setCookie: function (model, params) {
            var dayDiff = new Date(params.expires_in*1000) - new Date();
            dayDiff = dayDiff / (24*3600*1000);
            console.log(params);
            $.cookie('token', params.access_token, { expires: parseInt(dayDiff) });
            $.cookie('user_id', params.user_id, { expires: parseInt(dayDiff) });

            if (params.role === 2) {
                $.cookie('isAdmin', 'true', { expires: parseInt(dayDiff) });
            }
            // Сохраняем роль пользоватлея
            App.cache.role = params.role;

            Backbone.history.navigate('timer', {trigger: true});
        },

        error: function (code) {
            console.log(code);
            this.trigger('message', code.message);
        }
    });

    App.Models.Signup = Backbone.Model.extend({
        initialize: function (params, test) {
            this.on('all', this.all);
            this.on('sync', this.login, this);
            this.on('error', this.error, this);
        },

        url: 'auth.signup',

        all: function (method, params, test) {
            console.log(method, params, test);
        },

        login: function (model, params) {
            console.log(params);

            var auth = new App.Models.Auth;

            auth.fetch({ params: {
                client_id: App.config.client_id,
                username: this.params.username,
                password: this.params.password
            }});

            return true;
        },

        error: function (data) {
            this.trigger('message', data.message);
        }
    });

    App.Views.Login = Backbone.View.extend({
        id: 'login-page-root',

        events: {
            'keypress .form-login input': 'updateOnEnterLoginForm',
            'keypress .form-signup input': 'updateOnEnterSignupForm',
            'click button#submit': "submit",
            // 'keydown .form-login input': ''
            'click button#button-signup': 'signupForm',
            'click button#button-login': 'loginForm',
            'click button#button-token': 'toggleToken',
            'click .login-bar__scoreboard': 'showRating',
            'click .login-page-scoreboard__close': 'showLoginForm'
        },

        initialize: function () {
            this.on('sync', this.setCookie, this);
            App.Views.Main.render(this.render().$el);

            var arr = ['12', '6', '902', '1303', '1301', '305', '907', '7', '602', '903', '1601', '4', '13', '15', '304', '11', '303', '901', '908', '904', '1001', '3', '5', '1400', '1003', '403', '302', '401', '503', '1603', '14', '2', '1', '1604', '1002', '1004', '906', '402', '17', '1100', '16', '1602', '905', '100', '1500', '18', '601', '10', '502', '1005', '1302', '306', '8', '307', '301', '200', '501', '1200', '9', '700'],
                rand = Math.floor(Math.random() * arr.length);

            console.log(this.$el);
            this.$el.find('.login-page-background').addClass('login-page-background_' + arr[rand]);
        },

        signupForm: function() {
            this.$el.find('.message').hide();
            this.$el.find('.form-login').hide();

            this.$el.find('.form-signup').show();
        },

        loginForm: function() {
            this.$el.find('.message').hide();
            this.$el.find('.form-login').show();

            this.$el.find('.form-signup').hide();
        },

        toggleToken: function () {
            var form_token = this.$el.find('.form-token'),
                form_team = this.$el.find('.form-team');

            console.log(form_token, form_team);
            if (form_token.hasClass('hidden')) {
                form_team.addClass('hidden');
                form_token.removeClass('hidden');
            }
            else {
                form_token.addClass('hidden');
                form_team.removeClass('hidden');
            }
        },

        disableInput: function () {
            this.$el.find('input').prop('disabled', false);
        },

        enableInput: function () {
            this.$el.find('input').prop('disabled', false);
        },

        submitSignup: function() {
            var signup = new App.Models.Signup;
            var params = {
                mail: this.$el.find('#inputSignupEmail').val(),
                username: this.$el.find('#inputSignupLogin').val(),
                password: this.$el.find('#inputSignupPassword').val(),
                token: this.$el.find('#inputSignupToken').val(),
                team: this.$el.find('#inputSignupTeamName').val()
            };

            this.disableInput();

            console.log(params);
            if (params.username == "") {
                this.message("Не введен логин");
                this.enableInput();
                return false;
            }

            if (params.password == "") {
                this.message("Не введен пароль");
                this.enableInput();
                return false;
            }

            if (params.mail == "") {
                this.message("Не введен электронный адрес");
                this.enableInput();
                return false;
            }
            console.log('SIGNUP');
            signup.params = params;
            signup.on('message', this.message, this);

            signup.fetch({ params: params });
            return false;
        },

        submitLogin: function() {
            console.log('submitLogin');
            var auth = new App.Models.Auth;
            var params = {
                client_id: App.config.client_id,
                username: this.$el.find('#inputEmail').val(),
                password: this.$el.find('#inputPassword').val()
            };

            if (params.username == "") {
                this.message("Не введен логин");
                return false;
            }

            if (params.password == "") {
                this.message("Не введен пароль");
                return false;
            }

            auth.fetch({ params: params });

            auth.on('message', this.message, this);
            return false;
        },

        submit: function (e) {
            e.preventDefault();
            var type = $(e.target).closest('.form').data('type');

            return type == 'login' ? this.submitLogin() : this.submitSignup();
        },

        showRating: function () {
            var self = this,
                el = self.$el.find('.login-page-scoreboard'),
                $login = $(".login-page");

            this.collection = new App.Collections.Users();

            this.listenTo(this.collection, "add", function (array) {
                el.find('.results').html(new EJS({url: '/static/templates/rating/ListItem.ejs'}).render({
                    myRole: App.cache.role,
                    user: array.attributes.response
                }));
            });

            this.collection.fetch({ params: { order: 'rating' }});

            setInterval(function () {
                self.collection.fetch({ params: { order: 'rating' }});
            }, 5000);

            $login.animate({
                opacity: 0
            }, 500, function() {
                $login.hide();
                el.animate({ opacity: 1 });
                el.show();

                el.css("position","absolute");
                el.css("top", Math.max(0, (($(window).height() - el.outerHeight()) / 2) + $(window).scrollTop()) + "px");
                el.css("left", Math.max(0, (($(window).width() - el.outerWidth()) / 2) + $(window).scrollLeft()) + "px");

                return true;
            });
        },

        showLoginForm: function () {
            var self = this,
                $el = self.$el.find('.login-page-scoreboard'),
                $login = self.$el.find('.login-page');

            $el.animate({
                opacity: 0
            }, 500, function () {
                $el.hide();
                $login.animate({ opacity: 1 });
                $login.show();
            })
        },

        updateOnEnterLoginForm: function(e) {
            if (e.keyCode == 13) this.submit(e);
        },

        updateOnEnterSignupForm: function(e) {
            if (e.keyCode == 13) this.submit(e);
        },

        message: function(text) {
            console.log(text);
            this.$el.find('.message').show().html(text);
        },

        render: function() {
            this.$el.html(new EJS({url: '/static/templates/login.ejs'}).render());

            return this;
        }
    });

    new App.Router();

    App.Events.on('start_game', function() {
        // Выключаем старый таймер
        clearTimeout(App.cache['timerStart']);
        console.log('Игра началась. Старт!');
        App.Events.trigger('game:start')
    });

    App.Events.on('end_game', function() {
        console.log('игра закончилась');
        // Выключаем старый таймер
        clearTimeout(App.cache['timerEnd']);

        //Timer.trigger('start:timer:end')
        Backbone.history.navigate('end', {trigger: true});
    });



});
