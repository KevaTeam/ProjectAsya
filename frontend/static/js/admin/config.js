define(['jquery', 'underscore', 'backbone', 'wrapper', 'moment', 'datetimepicker'], function ($, underscore, Backbone, wrapper, moment) {

    var currentTimeModel = Backbone.Model.extend({url: 'timer.current'});

    var startEndSettingModel = Backbone.Model.extend({
        url: 'timer.get',

        setMethod: function (method) {
            this.method = (method == 'set' ? 'set' : 'get');
            this.setUrl();
        },

        setUrl: function () {
            this.url = 'timer.' + this.method;
        }
    });

    var dateView = Backbone.View.extend({
        events: {
            'click .submit': 'update'
        },

        initialize: function () {
            // Обновляем время с сервера для точности
            this.currentTime = new currentTimeModel;
            this.currentTime.on('change', this.current, this);
            this.currentTime.fetch();

            this.updateTimeTimer = setInterval(function () {
                this.fetch();
            }.bind(this.currentTime), 10000);

            this.startEndSetting = new startEndSettingModel;
            this.startEndSetting.on('change', this.setStartEnd, this);
            this.startEndSetting.fetch({params: {key: 'datetime_start'}});
        },

        initForms: function () {
            var fields = ['start', 'end'];

            for (var index in fields) {
                this.$el.find('.config__datetime-' + fields[index]).datetimepicker({
                    locale: 'ru',
                    format: "DD-MM-YYYY HH:mm:ss",
                    defaultDate: new Date()
                });
            }
        },

        message: {
            hide: function () {
                this.$el.find('.success-message').hide();
            },
            show: function () {
                this.$el.find('.success-message').show();
            }
        },

        current: function (model) {
            var time = model.get('timestamp'),
                $el = this.$el.find('.current-time');

            clearTimeout(this.timer);

            this.timer = setInterval(function () {
                $el.text(moment.unix(time).format('D MMMM YYYY, HH:mm:ss'));

                time += 1;
            }, 1000);

            $el.text(moment(time * 1000).format('D MMMM YYYY, HH:mm:ss'));
        },

        setStartEnd: function (model) {
            var fields = ['start', 'end'];

            for (var index in fields) {
                this.$el.find('.config__datetime-' + fields[index]).datetimepicker({
                    locale: 'ru',
                    format: "DD-MM-YYYY HH:mm:ss"
                });

                this.$el.find('.config__datetime-' + fields[index]).data("DateTimePicker").date(moment(model.get(fields[index]).date));
            }
        },

        update: function () {
            var setTimer = Backbone.Model.extend({url: 'timer.set'});
            timer = new setTimer();
            timer.fetch({
                params: {
                    start: this.$el.find('.config__datetime-start').val(),
                    end: this.$el.find('.config__datetime-end').val()
                }
            });

            this.$el.find('.success-message').hide();

            this.listenTo(timer, 'sync', function () {
                this.$el.find('.success-message').show();
            }, this);
        },

        render: function () {
            this.template = _.template($('#date-template').html());
            this.$el.html(this.template());

            this.initForms();

            return this;
        }
    });

    return Backbone.View.extend({
        el: '.container',
        template: new EJS({url: '/static/templates/admin/config/main.ejs'}).text,

        destructTimer: function () {
            clearInterval(this.currentTime.timer);
            clearInterval(this.updateTimeTimer);
        },

        initialize: function () {
            var self = this;

            wrapper.updateMenu('config');
            wrapper.renderPage(this.template.replace('<% token %>', $.cookie('token')));

            var date = new dateView();
            this.$el.find('.config__date').append(date.render().el);

            App.Events.on('page:update', this.destructTimer, this);

            moment.locale('ru');
        }
    });
});