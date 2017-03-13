define(['backbone', 'wrapper'], function(Backbone, wrapper) {
    return Backbone.Router.extend({
        initialize: function() {
            console.log('okey, router');

            Backbone.history.start();
        },

        routes: {
            '': 'index',
            'category': 'category',
            'config': 'config',
            'index': 'index',
            'quest': 'quest',
            'service': 'service',
            'messages': 'message',
            'users': 'users',
            'teams': 'teams',
            'users/:id': 'users'
        },
     
        index: function() {
            var html = new EJS({url: 'static/templates/admin/monitor/main.ejs'}).text;

            wrapper.renderPage(html);
            require(['monitor'], function(monitor) {
                new monitor();
            });
        },
        users: function() {
            require(['users'], function(users) {
                new users();
            });
        },
        quest: function() {
            require(['quest'], function(quest) {
                new quest();
            });
        },

        service: function() {
            require(['service'], function(service) {
                new service();
            });
        },

        config: function() {
            require(['config'], function(config) {
                new config();
            });
        },

        message: function() {
            require(['message'], function(message) {
                new message();
            });
        },

        category: function() {
            require(['category'], function(category) {
                new category();
            });
        },

        teams: function() {
            require(['team'], function(team) {
                new team();
            });
        }
    });
});