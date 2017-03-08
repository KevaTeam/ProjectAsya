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

        url: 'jury.get',

        parse: function (data) {
            return data['settings'];
        },

        setMethod: function(method) {
            this.method = (method == 'get' ? 'get' : 'set');
            this.setUrl();
        },

        setUrl: function(string) {
            this.url = 'jury.' + (string || this.method);
        }

    });

    return Backbone.View.extend({
        el: '.container',
        template: new EJS({url: 'static/templates/admin/config/main.ejs'}).text,
        events: {
            "click .submit-datetime": 'changeDate',
            "click .submit-flags": 'changeFlags'
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

        changeFlags: function() {
            this.$el.find('.success-message').hide();
            var date = new dataSetting('set');

            date.fetch({ params: { key: 'lifetime', value: this.$el.find('#lifetime input').val() } });
            date.fetch({ params: { key: 'port', value: this.$el.find('#flags_port input').val() } });

            var self = this;

            this.listenTo(date, 'sync', function() {
                self.$el.find('.success-message').show();
            });
        },

        setData: function(data) {
            console.log(data);
            this.$el.find('#round_length input').val(data.get('round_length'));
            this.$el.find('#lifetime input').val(data.get('flags').lifetime);

            this.$el.find('#flags_port input').val(data.get('flags').port);
            //$('#'+data.get('k')).datetimepicker({
            //    locale: 'ru',
            //    format: "DD-MM-YYYY HH:mm:ss",
            //    defaultDate: moment(data.get('value'), 'DD-MM-YYYY HH:mm:ss')
            //});
        },

        destructTimer: function() {
            clearInterval(this.timer);
        },

        initialize: function() {
            var self = this;

            wrapper.updateMenu('config');

            wrapper.renderPage(this.template);

            this.currentTime = new currentTime();
            this.data = new dataSetting('get');

            this.listenTo(this.data, 'sync', this.setData);

            // Обновляем время с сервера для точности
            setInterval(function () {
                this.currentTime.fetch();
            }.bind(this), 1000);
            this.currentTime.fetch();

            this.data.fetch({ params: { key: 'datetime_start' }});

            App.Events.on('page:update', function() {
                self.destructTimer();
            });

            moment.locale('ru');
        }
    });
});