define(['underscore', 'backbone'], function(_, Backbone) {
    var answer = Backbone.Model.extend({
        isCorrect: function() {
            return this.get('user_answer').toLowerCase() == this.get('real_answer').toLowerCase();
        }
    });

    var collection = Backbone.Collection.extend({
        url: 'quest.attempts',

        model: answer,

        parse: function(response) {
            return _.map(response, function(num, key) {
                // Делаем нумерацию рейтинга
                num['id'] = num['user']+'_'+num['quest']['id']+'_'+num['time'];
                return num;
            });
        }
    });

    return new collection();
});