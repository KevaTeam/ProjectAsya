define(['jquery', 'underscore', 'backbone', 'wrapper', 'selectize', 'bootstrap'], function($, _, Backbone, wrapper) {

    // Quests
    App.Models.Quest = Backbone.Model.extend({
        defaults: {
            id: 0,
            title: '',
            score: '',
            tags: '',
            author: '',
            short_text: '',
            full_text: '',
            solution: '',
            answer: '',
            type: 'add',
            section: {
                id: '0',
                name: ''
            }
        },

        parse: function(response) {
            response.type = 'edit';
            response.tags = response.tags.join(',');

            return response;
        }
    });

    App.Collections.ListQuest = Backbone.Collection.extend({
        url: 'quest.list',

        model: App.Models.Quest,

        parse: function(response) {
            return response.items;
        }
    });

    App.Models.QuestSection = Backbone.Model.extend({
        parse: function(response) {
            return response;
        }
    });

    App.Collections.ListSection = Backbone.Collection.extend({
        url: 'category.list',

        model: App.Models.QuestSection,

        parse: function(response) {
            return response.items;
        }
    });

    App.Views.QuestForm = Backbone.View.extend({
        events: {
            'click .btn-success': 'submit'
        },

        initialize: function () {
            this.template = _.template($('#quest-form-template').html());
        },

        remove: function () {
            this.$el.remove();
        },

        setTags: function () {
            var $selectize = this.$el.find('#inputTags').selectize({
                plugins: ['remove_button'],
                delimiter: ',',
                persist: false,
                create: function(input) {
                    return {
                        value: input,
                        text: input
                    }
                }
            });
        },

        submit: function() {
            var params = {
                    id: this.$el.find('#inputId').val(),
                    title: this.$el.find('#inputName').val(),
                    section: this.$el.find('#inputSection').val(),
                    score: this.$el.find('#inputScore').val(),
                    answer: this.$el.find('#inputAnswer').val(),
                    author: this.$el.find('#inputAuthor').val(),
                    short_text: this.$el.find('#inputShortDescription').val(),
                    full_text: this.$el.find('#inputDescription').val(),

                    tags: this.$el.find('#inputTags').val(),

                    solution: this.$el.find('#inputSolution').val()
                },
                type = this.$el.find('#inputType').val(),
                url = 'quest.' + (type == 'add' ? 'create':'save'),
                self = this;

            var model = Backbone.Model.extend({
                url: url,

                parse: function() {
                    self.remove();
                    App.Events.trigger('quests:list:update');
                }
            });
            var formModel = new model();

            formModel.fetch({
                method: 'POST',
                params: params
            });

            this.listenTo(formModel, 'error', function(response) {
                App.Events.trigger('quests:form:message:show', response.message);
            });
        },

        render: function() {
            this.$el.html(this.template(this.model.toJSON()));

            this.setTags();

            return this;
        }
    });

    App.Views.QuestList = Backbone.View.extend({
        tagName: 'tr',

        events: {
            'click .edit-quest': 'showEditForm',
            'click .delete-quest': 'deleteForm'
        },

        initialize: function() {
            this.template = _.template($('#quest-template').html());
        },

        showEditForm: function(el) {
            App.Events.trigger('quests:block:edit:show', $(el.currentTarget).data('id'));
        },

        deleteForm: function(el) {
            App.Events.trigger('quests:modal:confirm:show', $(el.currentTarget).data('id'));
        },

        render: function() {
            this.$el.html(this.template(this.model.toJSON()));
            return this;
        }
    });

    return Backbone.View.extend({
        el: '.container',

        events: {
            'click .quest-add': 'showForm'
        },

        initialize: function() {
            wrapper.updateMenu('quest');

            var html = new EJS({url: '/static/templates/admin/quests/main.ejs'}).text;

            wrapper.renderPage(html);

            this.blocks = {
                quests: this.$el.find('#quest-list'),
                form: this.$el.find('#quest-form')
            };

            // Список категорий квеста
            this.sections = [];

            this.collections = {};
            this.collections.Quests = new App.Collections.ListQuest();
            this.collections.Sections = new App.Collections.ListSection();


            this.collections.Quests.fetch();
            this.collections.Sections.fetch();

            this.listenTo(this.collections.Quests, 'sync', this.updateCount);
            this.listenTo(this.collections.Quests, 'add', this.addOneQuest);
            this.listenTo(this.collections.Quests, 'change', this.updateOneQuest);

            this.listenTo(this.collections.Sections, 'add', this.addOneSection);

            App.Events.on('quests:block:edit:show', this.showForm, this);
            App.Events.on('quests:modal:confirm:show', this.showDeleteWindow, this);
            App.Events.on('quests:list:update', this.updateList, this);
            App.Events.on('quests:form:message:show', this.showFormMessage, this);
        },

        showForm: function(id) {
            if(typeof(id) == 'object') {
                var model = new App.Models.Quest();
            }
            else {
                var model = this.collections.Quests.get(id);
            }

            // Добавляем список категорий
            model.attributes.listSection = this.sections;

            var view = new App.Views.QuestForm({ model: model });

            this.blocks.form.html(view.render().el);
        },

        updateList: function () {
            this.collections.Quests.fetch();
        },

        updateOneQuest: function(user) {
            var view = new App.Views.QuestList({ id: 'quest-'+user.get('id'), model: user});

            this.$el.find('#quest-'+user.get('id')).replaceWith(view.render().el);
        },

        addOneSection: function(model) {
            this.sections.push(model.toJSON());
        },

        showDeleteWindow: function(questId) {
            var model = Backbone.Model.extend({}),
                self = this;

            var modal = new App.Views.Modal({ model: new model({ 'questId': questId })});

            var modalWindow = this.$el.find('.modalWindow').html(modal.render().el).find('.modal');
            modalWindow.modal('show');

            this.listenTo(modal, 'submit', function() {
                var model = Backbone.Model.extend({
                    url: 'quest.delete',
                    parse: function(response){
                        var c = self.collections.Quests.get(questId);
                        self.collections.Quests.remove(c);
                        self.updateCount(self.collections.Quests);
                        self.$el.find('#quest-'+questId).remove();
                        modalWindow.modal('hide');
                    }
                });

                model = new model();
                model.fetch({ params: { id: questId } });
                self.listenTo(model, 'error', function(response) {
                    alert('Error! ' + response.message);
                });
            });
        },

        showFormMessage: function(text) {
            this.$el.find('.form-message').show().text(App.Functions.Message(text));
        },

        addOneQuest: function(model) {
            var view = new App.Views.QuestList({ id: 'quest-'+model.get('id'), model: model});

            this.blocks.quests.append(view.render().el);
        },

        updateCount: function (items) {
            var count_user = rulesRus(items.length, ['квест', 'квеста', 'квестов']);
            this.$el.find('.count_quest').text(count_user);
        }
    });

});
