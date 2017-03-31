define(['jquery', 'underscore', 'backbone', 'wrapper', 'moment', 'datetimepicker'], function($, underscore, Backbone, wrapper, moment) {

    var currentTime = Backbone.Model.extend({
        url: 'timer.current',
        timer: null,
        parse: function (response) {
            var time = response.timestamp,
                $el = $('.current-time');

            clearTimeout(this.timer);

            this.timer = setInterval(function() {
                $el.text(moment.unix(time).format('D MMMM YYYY, HH:mm:ss'));

                time += 1;
            }, 1000);

            $el.text(moment(time * 1000).format('D MMMM YYYY, HH:mm:ss'));
        }
    });

    var dataSetting = Backbone.Model.extend({
        initialize: function(method) {
            this.setMethod(method);
        },

        url: 'timer.get',

        parse: function (data) {
            var fields = ['start', 'end'];

            for (var index in fields) {
                $('.config__datetime-' + fields[index]).datetimepicker({
                    locale: 'ru',
                    format: "DD-MM-YYYY HH:mm:ss",
                    defaultDate: moment('08-12-2017 22:59:59', 'DD-MM-YYYY HH:mm:ss')
                });
            }
        },

        setMethod: function (method) {
            this.method = (method == 'get' ? 'get' : 'set');
            this.setUrl();
        },

        setUrl: function () {
            this.url = 'timer.' + this.method;
        }
    });

    return Backbone.View.extend({
        el: '.container',
        template: new EJS({url: '/static/templates/admin/config/main.ejs'}).text,
        events: {
            "click .submit-datetime": 'changeDate'
        },

        changeDate: function() {
            this.$el.find('.success-message').hide();
            var date = new dataSetting('set');
            date.fetch({ params: { key: 'datetime_start', value: this.$el.find('#datetime_start input').val() } });
            date.fetch({ params: { key: 'datetime_end', value: this.$el.find('#datetime_end input').val() } });
            
            var self = this;

            this.listenTo(date, 'sync', function() {
                self.$el.find('.success-message').show();
            });
        },

        destructTimer: function() {
            clearInterval(this.currentTime.timer);
            clearInterval(this.updateTimeTimer);
        },

        initialize: function() {
            var self = this;

            wrapper.updateMenu('config');
            wrapper.renderPage(this.template);

            // Обновляем время с сервера для точности
            this.currentTime = new currentTime();
            this.currentTime.fetch();
            this.updateTimeTimer = setInterval(function () {
                this.fetch();
            }.bind(this.currentTime), 10000);

            this.data = new dataSetting('get');
            this.data.fetch({ params: { key: 'datetime_start' }});

            App.Events.on('page:update', this.destructTimer, this);

            moment.locale('ru');
        }
    });
});