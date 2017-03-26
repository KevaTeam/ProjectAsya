define(['jquery', 'underscore', 'backbone', 'wrapper', 'selectize', 'bootstrap'], function ($, _, Backbone, wrapper) {

    var Message = Backbone.Model.extend({
        defaults: {
            'id': 0,
            'type': 0,
            'title': '',
            'text': "",
            'user': '',
            'time': new Date()
        }
    });

    var List = Backbone.Collection.extend({
        url: 'message.list',

        model: Message,

        parse: function (response) {
            return response.items;
        }
    });

    App.ViewsList = Backbone.View.extend({
        tagName: 'tr',

        events: {
            'click .edit_button': 'showEditForm',
            'click .delete_button': 'showConfirmModal'
        },

        initialize: function () {
            this.template = _.template($('#item-template').html());
        },
        // Обработка нажатия кнопки редактировать
        showEditForm: function (el) {
            App.Events.trigger('message:form:edit:show', el);
        },
        // Обработка нажатия кнопки удалить
        showConfirmModal: function (el) {
            App.Events.trigger('message:modal:confirm:show', $(el.currentTarget).data('id'));
        },

        render: function () {
            this.$el.html(this.template(this.model.toJSON()));
            return this;
        }
    });

    App.Views.Form = Backbone.View.extend({
        el: '.inputForm',

        events: {
            'change #inputType': 'updateType'
        },

        initialize: function () {
            this.template = _.template($('#form-template').html());

            this.selectize = {
                valueField: 'id',
                labelField: 'name',
                searchField: 'name',
                create: false,
                load: function (query, callback) {
                    if (!query.length) return callback();
                    $.ajax({
                        url: '/api/method/user.search',
                        type: 'POST',
                        data: {
                            'name': encodeURIComponent(query),
                            'access_token': $.cookie('token')
                        },
                        error: function () {
                            callback();
                        },
                        success: function (res) {
                            callback(res.response.slice(0, 10));
                        }
                    });
                },
                render: {
                    option: function (item, escape) {
                        return '<div><span class="title">' + item.name + '</span></div>';
                    }
                }
            };
        },

        updateType: function (e) {
            var $el = $(e.target),
                selectedValue = $el.find(':selected').val();

            if (selectedValue == 2) {
                this.$el.find('.block-user').removeClass('hidden');
            }
            else {
                this.$el.find('.block-user').addClass('hidden');
            }
        },

        show: function () {
            this.$el.show();
        },

        render: function () {
            this.$el.html(this.template(this.model.toJSON()));

            this.$el.find('#inputUser').selectize(this.selectize);
            return this;
        }
    });

    return Backbone.View.extend({
        el: '.container',

        events: {
            'click .add': 'showAddForm',
            'click .form-submit': 'addItem',
            'click .edit-form': 'showFormWithEdit'
        },

        initialize: function () {
            wrapper.updateMenu('message');

            this.collection = new List();

            // Получаем количество пользователей
            this.listenTo(this.collection, 'sync', this.updateCount);
            this.listenTo(this.collection, 'add', this.addItemToList);
            this.listenTo(this.collection, 'remove', this.removeOneUser);
            this.listenTo(this.collection, 'change', this.updateOneUser);

            // Обновление информации
            this.collection.fetch();

            // обнуляем обновление таймеров
            App.Events.on('page:update', this.destructTimer(), this);

            App.Events.on('message:form:edit:show', this.showFormWithEdit, this);
            App.Events.on('message:modal:confirm:show', this.showConfirmModal, this);
            App.Events.on('message:form:message:show', this.showFormMessage, this);

            this.render();
        },

        updateCount: function (items) {
        },

        tryCatch: function (str) {
            console.log(str);
        },

        updateOneUser: function (user) {
            var view = new App.ViewsList({id: 'user-' + user.get('id'), model: user});

            this.block.list.find('#message-' + user.get('id')).replaceWith(view.render().el);
        },

        // Показываем форму
        showForm: function (el) {
            this.block.form.append(el).show();
        },

        showAddForm: function () {
            var form = new App.Views.Form({model: new Message()});

            this.showForm(form.render().el);
        },

        showFormWithEdit: function (el) {
            var model = this.collection.get($(el.currentTarget).data('id'));

            var form = new App.Views.Form({model: model});
            this.showForm(form.render().$el);
        },

        showConfirmModal: function (userId) {
            var model = Backbone.Model.extend({}),
                self = this;

            var modal = new App.Views.Modal({model: new model({'id': userId})});

            var modalWindow = this.$el.find('.modalWindow').html(modal.render().el).find('.modal');
            modalWindow.modal('show');

            this.listenTo(modal, 'submit', function () {
                var model = Backbone.Model.extend({
                    url: 'message.delete',
                    parse: function (response) {
                        var c = self.collection.get(userId);
                        self.collection.remove(c);
                        modalWindow.modal('hide');
                    }
                });

                model = new model();
                model.fetch({params: {id: userId}});
                self.listenTo(model, 'error', function (response) {
                    alert('Error! ' + response.message);
                });
            });
        },

        showFormMessage: function (text) {
            this.$el.find('.form-message').show().text(text);
        },

        addItemToList: function (model) {
            var view = new App.ViewsList({id: 'message-' + model.get('id'), model: model});

            this.block.list.append(view.render().el);
        },

        removeOneUser: function (user) {
            this.block.list.find('#message-' + user.id).remove();
            this.updateCount(this.$el.find('#list tr'));
            return true;
        },

        addItem: function () {
            var params = {
                    id: this.$el.find('#inputId').val(),
                    title: this.$el.find('#inputTitle').val(),
                    text: this.$el.find('#inputText').val(),
                    user: this.$el.find('#inputUser').val(),
                    type: this.$el.find('#inputType').val()
                },
                self = this,
                isNew = (params.id == 0);

            var model = Backbone.Model.extend({
                url: 'message.' + (isNew ? 'add' : 'edit'),

                parse: function (response) {
                    self.listenToOnce(self.collection, (isNew ? 'add' : 'change'), function (model) {
                        self.$el.find('.sidebar').hide();
                    });

                    self.collection.fetch();
                }
            });

            model = new model();
            model.fetch({params: params});

            this.listenTo(model, 'error', function (response) {
                App.Events.trigger('users:form:message:show', response.message);
            });

        },

        destructTimer: function () {
            clearInterval(this.timerUsersList);
        },

        render: function () {
            var html = new EJS({url: 'static/templates/admin/messages/main.ejs'}).text;

            wrapper.renderPage(html);

            this.block = {
                list: this.$el.find("#list"),
                form: this.$el.find('.inputForm')
            };
        }
    });
});