requirejs.config({
    baseUrl: 'static/js/admin',
    paths: {
        app: '../app',
        ace: '//ace.c9.io/build/src/ace',
        jquery: '../vendors/jquery.min',
        'jquery.cookie': '../vendors/jquery.cookie',
        backbone: '../vendors/backbone-min',
        bootstrap: '../vendors/bootstrap.min',
        underscore: '../vendors/underscore-min',
        ejs: 'ejs',
        moment: '../vendors/moment',
        datetimepicker: '../vendors/datetimepicker',
        selectize: '../../node_modules/selectize/dist/js/selectize',
        sifter: '../../node_modules/sifter/sifter',
        microplugin: '../../node_modules/microplugin/src/microplugin',

        helpers: 'admin/helpers/helpers'
    }
});

requirejs(['main']);