/*!
 * jscim - javascript Library v0.8.0
 * https://github.com/ES-DOC/jscim
 *
 * Copyright 2012, ES-DOC (http://es-doc.org)
 *
 * Licensed under the following licenses:.
 *     CeCILL       http://www.cecill.info/licences/Licence_CeCILL_V2-en.html
 *     GPL v3       http://www.gnu.org/licenses/gpl.html
 *
 * Date: Fri 27 Jul 2012 13:53:33 UTC
 */

// ECMAScript 5 Strict Mode
"use strict";

// --------------------------------------------------------
// $jq :: JQuery nonconflict reference.
// See :: http://www.tvidesign.co.uk/blog/improve-your-jquery-25-excellent-tips.aspx#tip19
// --------------------------------------------------------
window.$ = window.$jq = jQuery.noConflict();

// --------------------------------------------------------
// cim :: Main cim object exposes various utility functions.
// --------------------------------------------------------
(function() {
    
    // Module variables.
    var root = this, events;

    // Global event dispatcher.
    events = _.extend({}, Backbone.Events);

    // Event handler for global errors.
    // @error       Error being reported.
    events.on("global:error", function (error) {
        // Format errors collection.
        if ( _.isUndefined(error.errors) ) {
            error.errors = "An unknown error has occurred.  If this persists please contact jscim @ github";
        }
        if ( _.isArray(error.errors) == false ) {
            error.errors = [error.errors];
        }

        // Create exception.
        var ex = Error();
        ex.name = 'JS-CIM v{0} - {1} - {2} Error';
        ex.name = ex.name.replace('{0}', root.CIM.utils.constants.app.VERSION);
        ex.name = ex.name.replace('{1}', error.type);
        ex.name = ex.name.replace('{2}', error.subType);
        ex.message = _.reduce(error.errors, function (memo, msg) {
            return memo + msg + '\n';
        }, '');

        // Fire exception event.
        events.trigger("cim:exception", ex);
    });

    // Create reference to the public object.
    if ( _.isUndefined(root.CIM) ) {
        root.CIM = root.cim = {
            events : events,
            utils : {
                views : {}
            }
        };
    }
    
}).call(this);

// --------------------------------------------------------
// jscim.utils.constants - set of constants.
// --------------------------------------------------------
(function() {
    // Module level variables.
    var CIM = this.CIM;

    // Declare constants used within plugin.
    CIM.utils.constants = {
        app : {
            NAME : "ES-DOC CIM Viewer",
            VERSION : "0.8.0"
        },
        DEFAULT_SCHEMA : '1.5',
        DEFAULT_LANGUAGE : 'en',
        api : {
            BASE_URL : 'http://test.api.esdoc.webfactional.com',
            query : {
                DOCSET_BY_ID : '/1/query/documentSetByID',
                DOCSET_BY_EXTERNAL_ID : '/1/query/documentSetByExternalID',
                DOCSET_BY_DRS : '/1/query/documentSetByDRS',
                DOC_BY_ID : '/1/query/documentByID',
                DOC_BY_NAME : '/1/query/documentByName'
            }
        },
        http : {
            GET : 'GET',
            JSONP : 'jsonp',
            JSONP_CALLBACK_FN : 'onJSONPLoad'
        }
    };
	
}).call(this);


// --------------------------------------------------------
// jscim.utils.misc - miscellaneous utility functions.
// --------------------------------------------------------
(function() {
    // Module level variables.
    var CIM = this.CIM;

    // Denulls an object by replacing the null keyword with passed value.
    // @param   obj - object being denulled.
    // @param   newval - replacement null value.
    CIM.utils.denull = function( obj, newval ) {
        if (_.isArray(obj)) {
            _(obj).each(function (item) {
                CIM.utils.denull(item, newval);
            });
        }
        else if ($jq.isPlainObject(obj)) {
            _.each(_.keys(obj), function(key) {
                if (_.isNull(obj[key])) {
                    obj[key] = newval;
                }
                else if ($jq.isArray(obj[key])) {
                    _.each(obj[key], function (item) {
                        CIM.utils.denull(item, newval);
                    })                    
                }
                else if ($jq.isPlainObject(obj[key])) {
                    CIM.utils.denull(obj[key], newval);
                }
            });
        }
    };
	
}).call(this);


// --------------------------------------------------------
// jscim.utils.validation - schema information & utilty functions.
// --------------------------------------------------------
(function() {
    // Module level variables.
    var CIM = this.CIM;

    // Set of supported cim versions.
    CIM.utils.schemas = {
        // Supported schemas.
        supported : {
            '1.5' : {
                activity : ['numericalExperiment', 'simulationRun'],
                data : ['dataObject'],
                grids : ['gridSpec'],
                quality : [],
                shared : ['platform'],
                software : ['modelComponent']
            }
        },

        supported1 : [
        {
            version : '1.5',
            types : [
                {
                    name : 'cIM_Quality',
                    shortName : 'quality',
                    displayName : 'QC Record',
                    pkg : 'quality'
                },
                {
                    name : 'dataObject',
                    shortName : 'data',
                    displayName : 'Data',
                    pkg : 'data'
                },
                {
                    name : 'ensemble',
                    shortName : 'ensemble',
                    displayName : 'Ensemble',
                    pkg : 'activity'
                },
                {
                    name : 'gridSpec',
                    shortName : 'grid',
                    displayName : 'Grid',
                    pkg : 'grids'
                },
                {
                    name : 'modelComponent',
                    shortName : 'model',
                    displayName : 'Model',
                    pkg : 'software'
                },
                {
                    name : 'numericalExperiment',
                    shortName : 'experiment',
                    displayName : 'Experiment',
                    pkg : 'activity'
                },
                {
                    name : 'platform',
                    shortName : 'platform',
                    displayName : 'Platform',
                    pkg : 'shared'
                },
                {
                    name : 'simulationRun',
                    shortName : 'simulation',
                    displayName : 'Simulation',
                    pkg : 'activity'
                }
            ]
        }],

        // Determines whether CIM schema is supported or not.
        // @schema		CIM schema.
        isSupportedSchema : function ( schema ) {
            return _.isUndefined(_.find(this.supported1, function (s) {
                return s.version === schema;
            })) === false;
        },

        // Returns CIM schema definition.
        // @schema		CIM schema.
        getSchema : function ( schema ) {
            return _.find(this.supported1, function (s) {
                return s.version === schema;
            });
        },

        // Determines whether CIM document type is supported or not.
        // @schema		CIM schema.
        // @type		CIM type.
        isSupportedType : function ( schema, type ) {
            // False if invalid schema.
            if (this.isSupportedSchema(schema) === false) {
                return false;
            }

            // False if no matching type.
            schema = this.getSchema(schema);
            if (_.isUndefined(_.find(schema.types, function (t) {
                return t.name === type || t.shortName === type;
            }))) {
                return false;
            };

            // All tests passed therefore return true.
            return true;
        },

        // Returns CIM type definition.
        // @schema		CIM schema.
        // @type		CIM type.
        getType : function ( schema, type ) {
            var result;
            if (this.isSupportedType(schema, type)) {
                result = _.find(this.getSchema(schema).types, function (t) {
                    return t.name === type || t.shortName === type;
                });
            }
            return result;
        },

        // Returns cim schema information.
        // @version		Schema version.
        getSchemaInfo : function ( version ) {
            return _.find(this.supported1, function (schema) {
                return schema.version === version;
            });
        },

        // Returns cim package information.
        // @version		Schema version.
        // @pkg                 Package name.
        getPackageInfo : function ( version, pkgName ) {
            var schema;

            schema = this.getSchemaInfo(version);
            if (_.isUndefined(schema) === false) {
                return _.find(schema.packages, function (pkg) {
                    return pkg.name === pkgName;
                });
            }
            return undefined;
        },

        // Returns cim type information.
        // @version		Schema version.
        // @pkg                 Package name.
        // @typeName            Type name.
        getTypeInfo : function ( version, pkgName, typeName ) {
            var pkg;

            pkg = this.getPackageInfo(version, pkgName);
            if (_.isUndefined(pkg) === false) {
                return _.find(pkg.types, function (type) {
                    return type.name === typeName;
                });
            }
            return undefined;
        },

        // Returns document display name as inferred from cim type info.
        // @document		CIM document.
        getDocumentDisplayName : function ( document ) {
            var type, cimTypeInfo;

            if (_.isUndefined(document) === false) {
                cimTypeInfo = document.cimInfo.typeInfo;
                type = this.getTypeInfo(cimTypeInfo.schema, cimTypeInfo.pkg, cimTypeInfo.type);
                if (_.isUndefined(type) === false) {
                    return type.displayName
                }
            }
            return undefined;
        }
    };
	
}).call(this);


// --------------------------------------------------------
// jscim.utils.validation - validation utilty functions.
// --------------------------------------------------------
(function() {
    // Module variables.
    var CIM = this.CIM,
        that = {},
        setError,
        are;
    
    // Either appends or throws an error.
    setError = function (errors, msg) {
        if (_.isUndefined(errors)) {
            errors = [];
        }
        if (_.isArray(errors)) {
            errors.push(msg);
        }        
        else {
            errors = [errors];
            errors.push(msg);
        }
    };
    
    // Validates that the set of fields are valid according to passed validator.
    are = function (fields, errors, validator) {
        if ( fields ) {
            _.each(fields, function(field) {
                validator(field[0], field[1], errors);
            })
        }
    }
    
    // Validates a required field.
    // @value		Value of field being validated.
    // @name		Name of field being validated.
    // @errors		Validation error collection.
    that.isRequired = function ( value, name, errors ) {
        var isValid;		// Is valid flag.
        var msg;			// Validation message.

        isValid = !_.isUndefined(value);		

        if ( !isValid )  {
            msg = 'Parameter {{0}} is required';
            msg = msg.replace('{0}', name);
            setError(errors, msg);
        }
        
        return isValid;
    }	
    
    // Validates a set of required fields.
    // @obj		Object being validated.
    // @fields		Set of required fields.
    // @errors		Validation error collection.
    that.areRequired = function ( obj, fields, errors ) {
        var msg = 'Parameter {{0}} is required';
        _.each(fields, function(field) {
            if (_.has(obj, field) === false) {
                setError(errors, msg.replace('{0}', field));
            }
        });
    };

    // Validates a set of string fields.
    // @obj		Object being validated.
    // @fields		Set of string fields.
    // @errors		Validation error collection.
    that.areStrings = function ( obj, fields, errors ) {
        var msg = 'Parameter {{0}} must be a string';
        _.each(fields, function(field) {
            if (_.has(obj, field) &&
                _.isString(obj[field]) === false) {
                setError(errors, msg.replace('{0}', field));
            }
        });
    }
			    
    // Validates a string field.
    // @value		Value of field being validated.
    // @name		Name of field being validated.
    // @errors		Validation error collection.
    that.isString = function ( value, name, errors ) {
        var isValid;		// Is valid flag.
        var msg;			// Validation message.
    	
        isValid = _.isString(value) && $jq.trim(value).length > 0;
    	
        if ( !isValid )  {
            msg = 'Parameter {{0}} must be a string';
            msg = msg.replace('{0}', name);
            setError(errors, msg);
        }
        
        return isValid;
    }	
    
    // Validates a set of string fields.
    // @fields		Set of fields being validated.
    // @errors		Validation error collection.
    that.areStrings = function ( fields, errors ) {
        are(fields, errors, that.isString);
    }      
    
    // Validates a plain object field.
    // @value		Value of field being validated.
    // @name		Name of field being validated.
    // @errors		Validation error collection.
    that.isPlainObject = function ( value, name, errors ) {
        var isValid;		// Is valid flag.
        var msg;			// Validation message.
		
        isValid = $jq.isPlainObject(value);
    	
        if ( !isValid )  {
            msg = 'Parameter {{0}} must be a hash of key/value pairs';
            msg = msg.replace('{0}', name);
            setError(errors, msg);
        }

        return isValid;
    }   
    
    // Validates a set of plain objects.
    // @fields		Set of fields being validated.
    // @errors		Validation error collection.
    that.arePlainObjects = function ( fields, errors ) {
        are(fields, errors, that.isPlainObject);
    }      
    
    // Validates passed CIM schema package type.
    // @schema		CIM schema.
    // @type		CIM schema package type.
    that.isCIMType = function ( schema, type, errors ) {
        var isValid, msg;
        isValid = CIM.utils.schemas.isSupportedType(schema, type);    		         	
        if (!isValid) {
            msg = 'Invalid cim document type :: {0} (schema = v{1}).';
            msg = msg.replace('{0}', type);
            msg = msg.replace('{1}', schema);
            setError(errors, msg);
        }
    	
        return isValid;
    };       

    // Register.
    CIM.utils.validation = that;
	
}).call(this);


// --------------------------------------------------------
// jscim.utils.views.dialog :: Helper encapulating displaying views as a modal dialog.
// --------------------------------------------------------
(function() {
    // Module variables.
    var CIM = this.CIM,
        View;

    // View class.
    View = Backbone.View.extend({
        render : function () {
            var me = this;
            
            // Instantiate dialog.
            this.$el.dialog({
                bgiframe: false,
                autoOpen: false,
                height : 'auto',
                width: '1000',
                position: ['center', 80],
                modal: true,
                resizable: false,
                close : function () {
                    if (_.isUndefined(me.options.onClose) === false &&
                        _.isFunction(me.options.onClose)) {
                        me.options.onClose();
                    }
                    me.remove();
                    me.$el.dialog('destroy');
                }
            });
        },

        // Append content to dialog.
        // @el   Dom element to be appended.
        append : function ( el ) {
            this.$el.append(el);
        },

        // Opens dialog for display.
        open : function () {
            this.$el.dialog('open');
        },

        // Set dialog title.
        // @caption       Title to be assigned.
        setTitle : function ( caption ) {
            var title = "";
            title = CIM.utils.constants.app.NAME;
            title += " v";
            title += CIM.utils.constants.app.VERSION;
            if (_.isUndefined(caption) === false) {
                title += " | ";
                title += caption;
            }
            this.$el.dialog('option', 'title', title);
        }
    });

    // Register view class.
    CIM.utils.views.DialogView = View;
	
}).call(this);


// --------------------------------------------------------
// jscim.utils.views.feedback - display feedback messages to user.
// --------------------------------------------------------
(function() {
    // Module variables.
    var CIM = this.CIM,
        MESSAGE_TYPE_INFORMATION = 1,
        MESSAGE_TYPE_CONFIRMATION = 2,
        MESSAGE_TYPE_PROGRESS = 3,
        MESSAGE_TYPE_HELP = 4,
        MESSAGE_TYPE_WARNING = 90,
        MESSAGE_TYPE_ERROR = 99,
        STANDARD_MESSAGE_UNKNOWN = "Unknown message",
        STANDARD_MESSAGE_ERROR = 'A processing error has occurred ... please contact the system administrator.',
        getTypeName,
        getClassName,
        getIconClassName,
        getTextClassName,
        View;

    // Returns name of type.
    // @type        Message type.
    getTypeName = function ( type ) {
        if (type === MESSAGE_TYPE_INFORMATION) {
            return 'information';
        }
        else if (type === MESSAGE_TYPE_CONFIRMATION) {
            return 'confirmation';
        }
        else if (type === MESSAGE_TYPE_HELP) {
            return 'help';
        }
        else if (type === MESSAGE_TYPE_WARNING) {
            return 'warning';
        }
        else if (type === MESSAGE_TYPE_ERROR) {
            return 'error';
        }
        else {
            return 'information';
        }
    };

    // Returns name of top level css class.
    // @type        Message type.
    getClassName = function( type ) {
        var typeName = getTypeName(type);
        return "cim-message cim-message-" + typeName;
    };

    // Returns name of icon related css class.
    // @type        Message type.
    getIconClassName = function( type ) {
        var typeName = getTypeName(type);
        return "cim-message-icon cim-message-icon-" + typeName;
    };

    // Returns name of text related css class.
    // @type        Message type.
    getTextClassName = function( type ) {
        var typeName = getTypeName(type);
        return "cim-message-text cim-message-text-" + typeName;
    };

    // View class.
    View = Backbone.View.extend({
        // Helper factory function.
        $make : function (tag, atts, text) {
            return $jq(this.make(tag, atts, text));
        },

        // Sets up ui in readiness for message to be displayed.
        // @type        Message type.
        setup : function (type) {
            var text, icon;

            // Set root element css.
            this.className = getClassName(type);

            // Inject message icon.
            icon = this.$make("div", { "class" : getIconClassName(type)});
            this.$el.append(icon);

            // Inject message text.
            text = this.$make( "div", { "class" : getTextClassName(type)});
            this.$el.append(text);
        },

        // Sets message text.
        // @type        Message type.
        // @text        Message text.
        setText : function (type, text) {
            if (_.isUndefined(text)) {
                if (type === MESSAGE_TYPE_ERROR) {
                    text = STANDARD_MESSAGE_ERROR;
                } else {
                    text = STANDARD_MESSAGE_UNKNOWN;
                }
            }
            this.$(".cim-message-text").text(text);
        },

        // Sets message caption.
        // @type        Message type.
        // @caption     Message caption.
        setCaption : function (type, caption) {
            var title = "";
            title = CIM.utils.constants.app.NAME;
            title += " - ";
            title += "v";
            title += CIM.utils.constants.app.VERSION;
            if (_.isUndefined(caption) === false) {
                title += " - ";
                title += caption;
            }
            this.$el.attr('title', title);
        },

        // Event handler for on dialog closed event.
        destroy : function () {
            this.$el.dialog('close');
            this.$el.dialog('destroy');
            this.remove();
        },

        // Returns message box configuration based on passed message type.
        // @type            Message type.
        // @continuation    Continuation function to be invoked if user responds in affirmative.
        createConfig : function (type, continuation) {
            var view = this, config;
            
            // Default.
            config = {
                width : 380,
                position: ['center', 150],
                modal: true
            };
            
            // Single button message.
            if (type === MESSAGE_TYPE_INFORMATION ||
                type === MESSAGE_TYPE_HELP ||
                type === MESSAGE_TYPE_WARNING ||
                type === MESSAGE_TYPE_ERROR) {
                _.extend(config, {
                    buttons : {
                        'OK': function () {
                            view.destroy();
                            if (_.isFunction(continuation)) {
                                continuation();
                            }
                        }
                    }
                })
            }

            // Two button message.
            if (type === MESSAGE_TYPE_CONFIRMATION) {
                _.extend(config, {
                    'Yes': function () {
                        view.destroy();
                        if (_.isFunction(continuation)) {
                            continuation();
                        }
                    },
                    'No': function () {
                        view.destroy();
                    }
                })
            }
            
            return config;
        },

        // Renders view.
        // @type            Message type.
        // @text            Message text.
        // @caption         Message caption.
        // @continuation    Message continuation function.
        render : function (type, text, caption, continuation) {
            // Set ui.
            this.setup(type);
            this.setText(type, text);
            this.setCaption(type, caption);

            // Open.
            this.$el.dialog(this.createConfig(type, continuation));
        }
    });

    // Handler for confirmation message event.
    // @text      Message text.
    CIM.events.on("message:confirmation", function (text, caption, continuation) {
        new View().render(MESSAGE_TYPE_CONFIRMATION, text, caption, continuation);
    });

    // Handler for error message event.
    // @text      Message text.
    CIM.events.on("message:error", function (text, caption, continuation) {
        new View().render(MESSAGE_TYPE_ERROR, text, caption, continuation);
    });

    // Handler for help message event.
    // @text      Message text.
    CIM.events.on("message:help", function (text, caption, continuation) {
        new View().render(MESSAGE_TYPE_HELP, text, caption, continuation);
    });

    // Handler for information message event.
    // @text      Message text.
    CIM.events.on("message:information", function (text, caption, continuation) {
        new View().render(MESSAGE_TYPE_INFORMATION, text, caption, continuation);
    });

    // Handler for warning message event.
    // @text      Message text.
    CIM.events.on("message:warning", function (text, caption, continuation) {
        new View().render(MESSAGE_TYPE_WARNING, text, caption, continuation);
    });

}).call(this);


// --------------------------------------------------------
// jscim.utils.views.fieldSet - a view over a set of name / value pairs.
// --------------------------------------------------------
(function() {
    // Module variables.
    var CIM = this.CIM,
        FieldSetView,
        FieldGroupView,
        FieldView;

    // View class - field set.
    FieldSetView = Backbone.View.extend({
        className : "cim-row-group ui-corner-all",
        render : function () {
            var fieldSet = this.options.fieldSet,
                mode = this.options.renderMode;

            // Ensure model is an array.
            if (_.isArray(fieldSet.model) === false) {
                fieldSet.model = [fieldSet.model];
            }

            // Render in appropriate mode.
            if (mode === 'column') {
                this._renderInlineView(fieldSet);

            } else {
                this._renderInlineView(fieldSet);
            }
            
            return this;
        },

        // Renders an inline view of a field set.
        // @fieldSet    Set of fields for rendering.
        _renderInlineView : function (fieldSet) {
            var fieldGroup,
                fieldGroupView,
                me = this;

            // Iterate model and inject field groups.
            _.each(fieldSet.model, function (model) {
                fieldGroup = {
                    model : model,
                    fields : fieldSet.fields
                };
                fieldGroupView = new FieldGroupView( { fieldGroup : fieldGroup });
                fieldGroupView.render();
                me.$el.append(fieldGroupView.$el);
            });
        },

        // Renders a columnar view of a field set.
        // @fieldSet    Set of fields for rendering.
        _renderColumnView : function (fieldSet) {
            var fieldGroup,
                fieldGroupView,
                me = this;

            // Iterate model and inject field groups.
            _.each(fieldSet.model, function (model) {
                fieldGroup = {
                    model : model,
                    fields : fieldSet.fields
                };
                fieldGroupView = new FieldGroupView( { fieldGroup : fieldGroup });
                fieldGroupView.render();
                me.$el.append(fieldGroupView.$el);
            });
        }
    });

    // View class - field group.
    FieldGroupView = Backbone.View.extend({
        className : "cim-row-group ui-corner-all",
        render : function () {
            var fieldGroup = this.options.fieldGroup;
            var fieldView;
            var me = this;

            // Iterate model/fields and inject accordingly
            _.each(fieldGroup.fields, function (field) {
                field.model = fieldGroup.model;
                fieldView = new FieldView( { field : field });
                fieldView.render();
                me.$el.append(fieldView.$el);
            });

            return this;
        }
    });

    // View class - field.
    FieldView = Backbone.View.extend({
        className : "cim-row",
        fieldHTML : "<div class='cim-cell-label'>\n\
                <span title='{title}'>{title}</span>\n\
            </div>\n\
            <div class='cim-cell-input'>\n\
                <span><%- {expression} %></span>\n\
            </div>",
        render : function () {
            var field = this.options.field;
            var html = this.fieldHTML;

            html = html.replace(/{title}/g, field.title);
            html = html.replace(/{expression}/g, field.expression);
            html = _.template(html)(field.model);
            this.$el.append(html);
            
            return this;
        }
    });

    // Register view classes.
    CIM.utils.views.FieldSetView = FieldSetView;
    CIM.utils.views.FieldGroupView = FieldGroupView;
    CIM.utils.views.FieldView = FieldView;
    
}).call(this);


// --------------------------------------------------------
// jscim.utils.views.nameValueSet - a view over a set of name / value pairs.
// --------------------------------------------------------
(function() {
    // Module variables.
    var CIM = this.CIM,
        NamedValueGroupSetView,
        NamedValueGroupView,
        NamedValueSetView,
        NamedValueView;

    // View class - named value group set.
    NamedValueGroupSetView = Backbone.View.extend({
        className : "cim-nv-groupset",
        render : function () {
            var model = this.options.model,
                view,
                me = this;

            // Ensure model is an array.
            if (_.isArray(model) === false) {
                model = [model];
            }

            _.each(model, function (group) {
                view = new NamedValueGroupView({
                    model : group
                });
                view.render();
                me.$el.append(view.$el);
            });
        }
    });

    // View class - named value group.
    NamedValueGroupView = Backbone.View.extend({
        className : "cim-nv-group",
        render : function () {
            var group = this.options.model,
                view,
                me = this;

            me.$el.append("<div class='title ui-state-highlight ui-corner-all'>{0}</div>".replace("{0}", group.title));
            view = new NamedValueSetView({
                model : group.namedValueSet
            });
            view.render();
            me.$el.append(view.$el);
        }
    });

    // View class - field set.
    NamedValueSetView = Backbone.View.extend({
        className : "cim-row-group ui-corner-all",
        render : function () {
            var nvSet = this.options.model,
                nvView,
                me = this;

            // Ensure model is an array.
            if (_.isArray(nvSet) === false) {
                nvSet = [nvSet];
            }

            // Sort.
            nvSet = _.sortBy(nvSet, 'name');

            _.each(nvSet, function (nv) {
                nvView = new NamedValueView( { model : nv } );
                nvView.render();
                me.$el.append(nvView.$el);                
            });
        }
    });

    // View class - field.
    NamedValueView = Backbone.View.extend({
        className : "cim-row",
        nvHTML : "<div class='cim-nv-name'>\n\
                <span title='{name}'>{name}</span>\n\
            </div>\n\
            <div class='cim-nv-value'>\n\
                <span>{value}</span>\n\
            </div>",
        render : function () {
            var nv = this.options.model;
            var html = this.nvHTML;

            html = html.replace(/{name}/g, nv.name);
            html = html.replace(/{value}/g, nv.value);
            this.$el.append(html);
            
            return this;
        }
    });

    // Register view classes.
    CIM.utils.views.NamedValueGroupSetView = NamedValueGroupSetView;
    CIM.utils.views.NamedValueGroupView = NamedValueGroupView;
    CIM.utils.views.NamedValueSetView = NamedValueSetView;
    CIM.utils.views.NamedValueView = NamedValueView;
    
}).call(this);


// --------------------------------------------------------
// jscim.utils.views.tabset :: a view over a set of tabs.
// --------------------------------------------------------
(function() {
    // Module variables.
    var CIM = this.CIM,
        View;

    // View class.
    View = Backbone.View.extend({
        // Backbone :: CSS class name.
        className : "cim-tabbed-view",

        // Backbone :: render function.
        render : function () {
            var $ul, $li, view = this;

            // Create dom.
            $ul = $jq(view.make("ul"));
            _.each(this.options.tabset, function(tab) {
                $ul.append($jq(this.make("li", {})).append(
                    $jq(this.make("a", {
                        "href" : "#" + tab.id,
                        "class" : tab.css === undefined ? "cim-tab-button" : tab.css
                    }, tab.title))
                ));
            }, this);

            // Reset dom.
            this.options.$contentWrapper.append(this.$el);
            this.$el.append($ul);
            this.$el.append(this.options.$content);

            // Create JQuery tab.
            this.$el.tabs({
                fx: {
                    opacity : 'toggle'
                }
            });
        }        
    });

    // Register view class.
    CIM.utils.views.TabsetView = View;

}).call(this);


// --------------------------------------------------------
// jscim.api.interface:: API public functions.
// --------------------------------------------------------
(function() {
    // Module variables.
    var CIM = this.cim,
        doQuery,
        parseDocumentSet;

    // Intiialise api hook.
    CIM.api = {};

    // Executes the query against backend api.
    // @params      Query parameters.
    // @query       Query handler.
    doQuery = function( params, query ) {
        var parseParams,
            validateParams,
            invokeAPI,
            onAPISuccess;

        // Default input parameters parser.
        parseParams = function () {
            params.project = $jq.trim(params.project);
            params.project = params.project.toUpperCase();
            _.defaults(params, {
                schema : CIM.utils.constants.DEFAULT_SCHEMA,
                language : CIM.utils.constants.DEFAULT_LANGUAGE
            });
        };

        // Default input parameters validator.
        validateParams = function () {
            return true;
        };

        // Callback invoked when api invocation succeeds.
        onAPISuccess = function (documentSet) {
            // Parse data.
            documentSet = parseDocumentSet(documentSet);

            // Trigger event.
            CIM.events.trigger("api:documentSetLoaded", documentSet);
        };

        // Invoke api.
        invokeAPI = function () {
            try {
                $jq.ajax({
                    type: CIM.utils.constants.http.GET,
                    url: query.getURL(),
                    data: query.getURLParams(),
                    dataType: CIM.utils.constants.http.JSONP,
                    jsonp: CIM.utils.constants.http.JSONP_CALLBACK_FN,
                    success: onAPISuccess
                });
            }
            catch (exception) {
                CIM.events.trigger("api:webServiceError", 'query', query.name, exception);
                return;
            }
        };

        // Main line.
        try {
            if ( validateParams() === true &&
                 query.validateParams() === true ) {
                parseParams();
                if (_.isFunction(query.parseParams)) {
                    query.parseParams();
                }
                invokeAPI();
            }
        }
        catch (exception) {
            CIM.events.trigger("api:error", 'query', query.name, exception);
        }
    };

    // Performs a parse over a set of documents returned from web service.
    // @documentSet       Set of documents to be parsed.
    parseDocumentSet = function ( documentSet ) {
        // Ensure documents are wrapped as an array.
        if ( _.isUndefined(documentSet) ) {
            documentSet = []
        }
        else if (_.isArray(documentSet) == false) {
            documentSet = [documentSet];
        }

        // Ensure all documents identifiable json.
        documentSet = _.map(documentSet, function(doc) {
            if (_.isObject(doc)) {
                return doc;
            } else {
                return JSON.parse(doc);
            }
        });

        // Ensure all documents identifiable cim documents.
        documentSet = _.filter(documentSet, function(doc) {
            return (_.has(doc, 'cimInfo') &&
                    _.has(doc.cimInfo, 'typeInfo') &&
                    _.has(doc.cimInfo.typeInfo, 'schema') &&
                    _.has(doc.cimInfo.typeInfo, 'package') &&
                    _.has(doc.cimInfo.typeInfo, 'type') );
        });

        // Extend document with helper variables/functions.
        _.each(documentSet, function(doc) {
            // Javascript key word issue.
            doc.cimInfo.typeInfo.pkg = doc.cimInfo.typeInfo['package'];

            // Document key.
            // TODO include lang
            doc.cimInfo.key = doc.cimInfo.project;
            doc.cimInfo.key += '_';
            doc.cimInfo.key += doc.cimInfo.typeInfo.schema;
            doc.cimInfo.key += '_';
            doc.cimInfo.key += doc.cimInfo.id;
            doc.cimInfo.key += '_';
            doc.cimInfo.key += doc.cimInfo.version;

            // Document type key.
            doc.cimInfo.typeKey = doc.cimInfo.typeInfo.schema;
            doc.cimInfo.typeKey += '-';
            doc.cimInfo.typeKey += doc.cimInfo.typeInfo.pkg;
            doc.cimInfo.typeKey += '-';
            doc.cimInfo.typeKey += doc.cimInfo.typeInfo.type;

            // Document display.
            doc.cimDisplayTitle = doc.cimInfo.project.toUpperCase();
            doc.cimDisplayTitle += ' ';
            doc.cimDisplayTitle += doc.cimInfo.typeInfo.typeDisplayName;
            doc.cimDisplayTitle += ' - ';
            doc.cimDisplayTitle += doc.shortName;
            doc.cimDisplayTitle += ' (v';
            doc.cimDisplayTitle += doc.cimInfo.version;
            doc.cimDisplayTitle += ')';
        });

        return documentSet;
    };

    // Gets a cim document set by external ID.
    // @params     	Query parameters.
    CIM.api.getByExternalID = function(params) {
        var query  = {};

        // Query name.
        query.name = 'getByExternalID';

        // Query parameter validation.
        query.validateParams = function () {
            var errors = [],
                fields = ['externalID', 'externalType', 'project', 'schema', 'language'];

            // Validate.
            if (CIM.utils.validation.isPlainObject(params, 'params', errors) == true) {
                CIM.utils.validation.areRequired(params, fields, errors);
                CIM.utils.validation.areStrings(params, fields, errors);
            }

            // Report errors.
            if (errors.length > 0) {
                CIM.events.trigger("api:error", errors);
            }

            return errors.length === 0;
        };

        // Query url factory.
        query.getURL = function () {
            var url;
            url = CIM.utils.constants.api.BASE_URL;
            url += CIM.utils.constants.api.query.DOCSET_BY_EXTERNAL_ID;
            url += '/' + params.project;
            url += '/' + params.externalType;
            url += '/' + params.externalID;
            return url;
        };

        // Query url parameter factory.
        query.getURLParams = function () {
            return {
                encoding : 'json',
                language : params.language,
                schema : params.schema
            }
        };

        // Invoke query.
        doQuery(params, query);
    };

    // Gets a cim document set by drs terms.
    // @params     	Query parameters.
    CIM.api.getByDRS = function(params) {
        var query  = {};

        // Query name.
        query.name = 'getByDRS';

        // Query parameter validation.
        query.validateParams = function () {
            var errors = [],
                fields = ['drsPath', 'schema', 'language'];

            // Validate.
            if (CIM.utils.validation.isPlainObject(params, 'params', errors) == true) {
                CIM.utils.validation.areRequired(params, fields, errors);
                CIM.utils.validation.areStrings(params, fields, errors);
            }

            // Report errors.
            if (errors.length > 0) {
                CIM.events.trigger("api:error", errors);
            }

            return errors.length === 0;
        };

        // Query parameter parsing.
        query.parseParams = function () {
            if (_.has(params, 'drsKeys') === false) {
                params.drsKeys = _.without(params.drsPath.split('/'), "");
            }
            params.drsPath = _.reduce(params.drsKeys, function (drsPath, drsKey) {
                return drsPath + '/' + $jq.trim(drsKey).toUpperCase();
            }, '');
        };

        // Query url factory.
        query.getURL = function () {
            var url;
            url = CIM.utils.constants.api.BASE_URL;
            url += CIM.utils.constants.api.query.DOCSET_BY_DRS;
            url += params.drsPath;
            return url;
        };

        // Query url parameter factory.
        query.getURLParams = function () {
            return {
                encoding : 'json',
                language : params.language,
                schema : params.schema
            }
        };

        // Invoke query.
        doQuery(params, query);
    };
	
    // Gets a cim document set by name.
    // @params     	Query parameters.
    CIM.api.getByName = function(params) {
        var query  = {};

        // Query name.
        query.name = 'getByName';

        // Query parameter validation.
        query.validateParams = function () {
            var errors = [],
                fields = ['project', 'type', 'name', 'schema', 'language'];

            // Validate params.
            if (CIM.utils.validation.isPlainObject(params, 'params', errors) == true) {
                CIM.utils.validation.areRequired(params, fields, errors);
                CIM.utils.validation.areStrings(params, fields, errors);
                if (errors.length === 0) {
                    CIM.utils.validation.isCIMType(params.schema, params.type, errors);
                }
            }

            // Report errors.
            if (errors.length > 0) {
                CIM.events.trigger("api:error", errors);
            }

            return errors.length === 0;
        };

        // Query parameter parsing.
        query.parseParams = function () {
            params.type = CIM.utils.schemas.getType(params.schema, params.type).name;
            params.type = params.type.toUpperCase();
            params.name = $jq.trim(params.name);
            params.name = params.name.toUpperCase();
        };

        // Query url factory.
        query.getURL = function () {
            var url;
            url = CIM.utils.constants.api.BASE_URL;
            url += CIM.utils.constants.api.query.DOC_BY_NAME;
            url += '/' + params.project;
            url += '/' + params.type;
            url += '/' + params.name;
            return url;
        };

        // Query url parameter factory.
        query.getURLParams = function () {
            return {
                encoding : 'json',
                language : params.language,
                schema : params.schema
            }
        };

        // Invoke query.
        doQuery(params, query);
    };

    // Gets a cim document set by id.
    // @params     	Query parameters.
    CIM.api.getByID = function(params) {
        var query  = {};

        // Query name.
        query.name = 'getByID';

        // Query parameter validation.
        query.validateParams = function () {
            var errors = []
                fields = ['id', 'version', 'target', 'project', 'schema', 'language'];

            // Validate params.
            if (CIM.utils.validation.isPlainObject(params, 'params', errors) == true) {
                CIM.utils.validation.areRequired(params, fields, errors);
                CIM.utils.validation.areStrings(params, fields, errors);
            }

            // Report errors.
            if (errors.length > 0) {
                CIM.events.trigger("api:error", errors);
            }

            return errors.length === 0;
        };

        // Query url factory.
        query.getURL = function () {
            var url;
            url = CIM.utils.constants.api.BASE_URL;
            if (params.target.toUpperCase() === 'DOCUMENT') {
                url += CIM.utils.constants.api.query.DOC_BY_ID;
            } else {
                url += CIM.utils.constants.api.query.DOCSET_BY_ID;
            }
            url += '/' + params.project;
            url += '/' + params.id;
            url += '/' + params.version;
            return url;
        };

        // Query url parameter factory.
        query.getURLParams = function () {
            return {
                encoding : 'json',
                language : params.language,
                schema : params.schema
            }
        };

        // Invoke query.
        doQuery(params, query);
    };    
	
}).call(this);


// --------------------------------------------------------
// jscim.api.events :: API event handlers.
// --------------------------------------------------------
(function() {		
    // Module variables.
    var CIM = this.CIM;

    // General error event handler.
    // @err         Error message.
    CIM.events.on("api:error", function(err) {
        var error;
        
        // Set error.
        error = {
            type : 'API',
            subType : 'General',
            errors : [err]
        };

        // Bubble event.
        CIM.events.trigger("global:error", error);
    });

    // Web service error event handler.
    // @service         Service raising in error.
    // @operation       Service operation in error.
    // @exception       Service exception.
    CIM.events.on("api:webServiceError", function(service, operation, exception) {
        var error, err;

        // Set error msg.
        err = "An error occurred when invoking a CIM web service:\n";
        err += "\tService\t: "+ service + "\n";
        err += "\tOperation\t: "+ operation + "\n";
        err += "\tError\t\t: " + exception.message + "\n";
        
        // Set error.
        error = {
            type : 'API',
            subType : 'Web Service',
            errors : [err]
        };

        // Bubble event.
        CIM.events.trigger("global:error", error);
    });

}).call(this);


// --------------------------------------------------------
// jscim.viewer.interface :: Viewer public functions.
// --------------------------------------------------------
(function() {		
    // Module variables.
    var CIM = this.cim;
    
    // Intiialise viewer hook.
    CIM.viewer = {
        views : {}
    };

    // Renders a CIM document view derived from results of a drs query.
    // @params     	Rendering parameters.
    CIM.viewer.renderFromDRS = function(params) {
        var validateParams,
            parseParams;

        // Validate params.
        validateParams = function() {
            var errors = [],
                fields = ['drsPath', 'project', 'schema', 'language'];

            // Validate.
            if (CIM.utils.validation.isPlainObject(params, 'params', errors) == true) {
                CIM.utils.validation.areRequired(params, fields, errors);
                CIM.utils.validation.areStrings(params, fields, errors);
            }

            // Report errors.
            if (errors.length > 0) {
                CIM.events.trigger("viewer:error", errors);
            }

            return errors.length === 0;
        };

        // Parse parameters.
        parseParams = function () {
            _.defaults(params, {
                schema : CIM.utils.constants.DEFAULT_SCHEMA,
                language : CIM.utils.constants.DEFAULT_LANGUAGE
            });
        };

        // If parsed params are valid then call API.
        parseParams();
        if ( validateParams() === true ) {
            CIM.api.getByDRS(params);
        }
    };

    // Renders a CIM document view derived from results of an external id query.
    // @params     	Rendering parameters.
    CIM.viewer.renderFromExternalID = function(params) {
        var validateParams,
            parseParams;

        // Validate params.
        validateParams = function() {
            var errors = [],
                fields = ['externalID', 'externalType', 'project', 'schema', 'language'];

            // Validate.
            if (CIM.utils.validation.isPlainObject(params, 'params', errors) == true) {
                CIM.utils.validation.areRequired(params, fields, errors);
                CIM.utils.validation.areStrings(params, fields, errors);
            }

            // Report errors.
            if (errors.length > 0) {
                CIM.events.trigger("viewer:error", errors);
            }

            return errors.length === 0;
        };

        // Parse parameters.
        parseParams = function () {
            _.defaults(params, {
                schema : CIM.utils.constants.DEFAULT_SCHEMA,
                language : CIM.utils.constants.DEFAULT_LANGUAGE
            });
        };

        // If parsed params are valid then call API.
        parseParams();
        if ( validateParams() === true ) {
            CIM.api.getByExternalID(params);
        }
    };

    // Renders a CIM document view derived from results of a name query.
    // @params     	Rendering parameters.
    CIM.viewer.renderFromName = function(params) {
        var validateParams,
            parseParams;

        // Validate params.
        validateParams = function() {
            var errors = [],
                fields = ['type', 'name', 'project', 'schema', 'language'];

            // Validate.
            if (CIM.utils.validation.isPlainObject(params, 'params', errors) == true) {
                CIM.utils.validation.areRequired(params, fields, errors);
                CIM.utils.validation.areStrings(params, fields, errors);
                if (errors.length === 0) {
                    CIM.utils.validation.isCIMType(params.schema, params.type, errors);
                }
            }

            // Report errors.
            if (errors.length > 0) {
                CIM.events.trigger("viewer:error", errors);
            }

            return errors.length === 0;
        };

        // Parse parameters.
        parseParams = function () {
            _.defaults(params, {
                schema : CIM.utils.constants.DEFAULT_SCHEMA,
                language : CIM.utils.constants.DEFAULT_LANGUAGE
            });
        };

        // If parsed params are valid then call API.
        parseParams();
        if ( validateParams() === true ) {
            CIM.api.getByName(params);
        }
    };

    // Renders a CIM document view derived from results of an id query.
    // @params     	Rendering parameters.
    CIM.viewer.renderFromID = function (params) {
        var validateParams,
            parseParams;

        // Validate parameters.
        validateParams = function() {
            var errors = [],
                fields = ['id', 'version', 'target', 'project', 'schema', 'language'];

            // Validate.
            if (CIM.utils.validation.isPlainObject(params, 'params', errors) == true) {
                CIM.utils.validation.areRequired(params, fields, errors);
                CIM.utils.validation.areStrings(params, fields, errors);
            }

            // Report errors.
            if (errors.length > 0) {
                CIM.events.trigger("viewer:error", errors);
            }

            return errors.length === 0;
        };

        // Parse parameters.
        parseParams = function () {
            _.defaults(params, {
                schema : CIM.utils.constants.DEFAULT_SCHEMA,
                language : CIM.utils.constants.DEFAULT_LANGUAGE
            });
        };

        // If parsed params are valid then call API.
        parseParams();
        if ( validateParams() === true ) {
            CIM.api.getByID(params);
        }
    };
		
}).call(this);




// --------------------------------------------------------
// jscim.viewer.events :: Viewer event handlers.
// --------------------------------------------------------
(function() {		
    // Module variables.
    var CIM = this.cim,
        uiResources;
    
    // User interface resources.
    uiResources = {
        nullField : '--',
        messages : {
            emptyDocumentSet : "No CIM metadata can be found at this time."
        }
    };

    // Event handler triggered whenever a viewer exception occurs.
    // @exception      An exception.
    CIM.events.on("viewer:exception", function (exception) {
        var error;

        // Set error.
        error = {
            type : 'Viewer',
            subType : 'Unknown',
            errors : [exception.message]
        };

        // Trigger event.
        CIM.events.trigger("global:error", error);
    });

    // Event handler triggered whenever a viewer error occurs.
    // @errors      Set of errors.
    CIM.events.on("viewer:error", function (errors) {
        var error;

        // Set error.
        error = {
            type : 'Viewer',
            subType : 'General',
            errors : errors
        };

        // Trigger event.
        CIM.events.trigger("global:error", error);
    });
    
    // Event handler triggered whenever api loads a document set.
    // @all         Set of all cim documents returned by api.
    CIM.events.on("api:documentSetLoaded", function (all) {
        var renderable;
        
        // N.B. Handle exceptions as this is a module boundary.
        try {
            // Exclude non-renderable documents.
            renderable = all.filter(function(document) {
                return CIM.viewer.views.DocumentView.isSupported(document);
            });

            // If there are no renderable documents trigger messaging event.
            if (renderable.length === 0) {
                CIM.events.trigger("message:information",
                                   uiResources.messages.emptyDocumentSet);
            }
            // Otherwise ...
            else  {
                // Format all documents prior to rendering.
                _.each(all, function (document) {
                    CIM.utils.denull(document, uiResources.nullField);
                });

                // Sort renderable documents prior to rendering.
                renderable = CIM.viewer.views.DocumentView.sortDocumentSet(renderable);

                // Trigger event.
                CIM.events.trigger("viewer:render", renderable, all);
            }
        }
        catch (exception) {
            CIM.events.trigger("viewer:exception", exception);
        }
    });

    // Event handler triggered whenever a document set is ready to be rendered.
    // @renderable  Set of renderable cim documents returned by api.
    // @all         Set of all cim documents returned by api.
    CIM.events.on("viewer:render", function (renderable, all) {
        var viewerOptions, viewer, dialog;

        // Initialise viewer.
        viewerOptions = {
            documents : {
                all : all,
                renderable : renderable,
                current : renderable[0]
            },
            documentSet : all
        };
        viewer = new CIM.viewer.views.DocumentViewport(viewerOptions);

        // Render view.
        viewer.render();

        // Initialise dialog.
        dialog = new CIM.utils.views.DialogView({
            onClose : function () {
                viewer.destroy();
            }
        });

        // Event handler triggered whenever user selects a document.
        CIM.events.on("viewer:documentSelected", function ( document, documentSet ) {
            dialog.setTitle(document.cimDisplayTitle);
        });

        // Render dialog.
        dialog.render();
        dialog.append(viewer.el);

        // Auto-select initial document.
        CIM.events.trigger("viewer:documentSelected", renderable[0], all);

        // Open dialog.
        dialog.open();
    });
		
}).call(this);




// --------------------------------------------------------
// jscim.viewer.views.core.main - primary cim docuemtn view
// --------------------------------------------------------
(function() {
    // Module variables.
    var CIM = this.cim,
        DocumentView;

    // CIM document view - extends Backbone.View.
    DocumentView = CIM.viewer.views.DocumentView = Backbone.View.extend(
    // ... instance members.
    {
        // Backbone : css class name.
        className : 'cim-document-outer',

        // Backbone : render.
        render : function () {
            var $document,
                documentView,
                ctx,
                renderers = [];

            // Initialize DOM.
            $document = this._initializeDOM();

            // Get document view.
            documentView = DocumentView.getView(this.options.documentType);

            // Set renderering context.
            ctx = {
                view : this,
                viewMetadata : documentView.metadata.create(),
                viewOptions : documentView.options.create(),
                make : this.make,
                $make : function (tagName, attributes, content) {
                    return $jq(this.make(tagName, attributes, content));
                },
                $document : $document,
                document : this.options.document,
                documentSet : this.options.documentSet
            };

            // Execute renderers (in order of priority).
            renderers = this._getRenderers(documentView.renderers, ctx);
            _.each(renderers, function(renderer) {
                renderer.task(ctx);
            });
        },

        // Initializes the DOM.
        _initializeDOM : function () {
            this.$document = $jq(this.make("div", {}));
            this.$document.attr('id', this.options.document.cimInfo.key);
            this.$document.addClass('cim-document');
            this.$document.addClass(this.options.documentType);
            this.$el.append(this.$document);
        },

        // Adds a document section to the document view.
        addSection : function (sectionName) {
            var sectionID, $section;
            
            sectionID = this.options.document.cimInfo.key.replace('.', '-');
            sectionID += '-';
            sectionID += sectionName;

            $section = $jq(this.make("div", {}));
            $section.attr('id', sectionID);
            $section.addClass('section');
            $section.addClass(sectionName);
            this.$document.append($section);
            
            return $section;
        },

        // Gets set of renderers for rendering.
        _getRenderers : function (viewRenderers, ctx) {
            var renderers = [];

            // Set renderers (i.e. all + documentView.renderers).
            _.each(DocumentView.getView('all').renderers, function (r) {
                renderers.push(r);
            });
            _.each(viewRenderers, function (r) {
                renderers.push(r);
            });

            // Filter by ui mode.
            renderers = _.filter(renderers, function (renderer) {
                return renderer.uiMode === 'all' ||
                       renderer.uiMode === ctx.viewOptions.mode;
            });

            // Filter by ui framework.
            // TODO
            renderers = _.filter(renderers, function (renderer) {
                return true;
            });

            // Filter by predicate if applicable.
            renderers = _.filter(renderers, function (renderer) {
                if (_.has(renderer, 'predicate') &&
                    _.isFunction(renderer.predicate)) {
                    return renderer.predicate(ctx);
                } else {
                    return true;
                }
            });

            return _.sortBy(renderers, "priority");
        }
    },
    // ... static members.
    {
        // Collection of document views.
        views : [],

        // Returns a document view from managed collection.
        // @documentType        Type of document for which a view is to be returned.
        getView : function (documentType) {
            var view;

            // Get view.
            view = _.find(this.views, function (view) {
                return view.documentType === documentType;
            });

            // Create if necessary.
            if (view === undefined) {
                view = {
                    documentType : documentType,
                    options : undefined,
                    metadata : undefined,
                    renderers : []
                }
                this.views.push(view);
            }

            return view;
        },

        // Determines whether a document has a corresponding view or not.
        isSupported : function (document) {
            var documentView;

            documentView = _.find(this.views, function (view) {
                return view.documentType === document.cimInfo.typeKey;
            });

            return documentView !== undefined;
        },

        // Registers set of document metadata factories.
        // @metadata        Metadata factory being registered.
        setMetadata : function (metadata) {
            var view;

            // Defensive programming.
            if (_.isObject(metadata) === false ||
                _.has(metadata, "documentType") === false ||
                _.isString(metadata.documentType) === false ||
                _.has(metadata, "create") === false ||
                _.isFunction(metadata.create) === false) {
                cimEvents.trigger("viewer:exception", 
                                  { message:'Invalid view metadata factory' });
                return;
            }
            
            // Get view & assign metadata.
            view = this.getView(metadata.documentType);
            view.metadata = metadata;
        },
        
        // Registers set of document view options.
        // @options         Options being registered.
        setOptions : function (options) {
            var view;

            // Defensive programming.
            if (_.isObject(options) === false ||
                _.has(options, "documentType") === false ||
                _.isString(options.documentType) === false ||
                _.has(options, "renderingOrder") === false ||
                _.isNumber(options.renderingOrder) === false ||
                _.has(options, "defaults") === false ||
                _.isObject(options.defaults) === false) {
                CIM.events.trigger("viewer:exception",
                                  { message:'Invalid view options' });
                return;
            }

            // Set defaults.
            _.defaults(options, {
                userOptions : undefined,
                parseUserOptions : function (userOptions) {
                    if ( _.isUndefined(userOptions) ) {
                        userOptions = this.defaults;
                    } else {
                        if ( $jq.isPlainObject(this.defaults) &&
                            _.isFunction(this.applyDefaults) ) {
                            this.applyDefaults(userOptions);
                        }
                    }
                    return userOptions;                    
                },
                // Factory method to create options at point of execution.
                create : function () {
                    return options.defaults;
                }
            });

            // Get view & assign options.
            view = this.getView(options.documentType);
            view.options = options;
        },

        // Registers a document view renderer.
        // @renderer        Renderer being registered.
        setRenderer : function (renderer) {
            var view;

            // Defensive programming.
            if (_.isObject(renderer) === false ||
                _.has(renderer, "documentType") === false ||
                _.isString(renderer.documentType) === false ||
                _.has(renderer, "task") === false ||
                _.isFunction(renderer.task) === false) {
                cimEvents.trigger("viewer:exception",
                                  { message:'Invalid document view renderer' });
                return;
            }

            // Set defaults.
            _.defaults(renderer, {
                priority : 10,
                uiMode : 'all',
                uiFramework : 'all'
            });

            // Get view & assign renderer.
            view = this.getView(renderer.documentType);
            view.renderers.push(renderer);
        },

        // Sorts set of documents by rendering order.
        // @documentSet     Document set being sorted.
        sortDocumentSet : function ( documentSet ) {
            return _.sortBy(documentSet, function (doc) {
                return this.getView(doc.cimInfo.typeKey).options.renderingOrder;
            }, this);
        }
    } );

}).call(this);



// --------------------------------------------------------
// jscim.viewer.views.core.mainRenderings - set of generic document rendering methods.
// --------------------------------------------------------
(function() {
    // Module variables.
    var CIM = this.cim,
        DocumentView = CIM.viewer.views.DocumentView;

    // View renderer (all) - set view sections.
    // @ctx     View rendering context.
    DocumentView.setRenderer({
        documentType : 'all',
        uiMode : 'all',
        task : function (ctx) {
            // Escape if unnecessary.
            if (_.has(ctx.viewOptions, 'sections') === false) {
                return;
            }

            ctx.viewSections = [];
            _.each(ctx.viewOptions.sections, function (vsOpt) {
                if (vsOpt.display === true) {
                    ctx.viewSections.push(ctx.viewMetadata[vsOpt.name]);
                }
            });
        }
    });

    // View renderer (all) - set view section model.
    // @ctx     View rendering context.
    DocumentView.setRenderer({
        documentType : 'all',
        uiMode : 'all',
        task : function (ctx) {
            _.each(ctx.viewSections, function(vs) {
                if (_.has(vs, 'filterModel') === true) {
                    vs.model = vs.filterModel(ctx.document);
                } else {
                    vs.model = ctx.document;
                }
            });
        }
    });

    // View renderer (all) - filter view sections.
    // @ctx     View rendering context.
    DocumentView.setRenderer({
        documentType : 'all',
        uiMode : 'all',
        task : function (ctx) {
            ctx.viewSections = _.filter(ctx.viewSections, function(vs) {
                if (_.isUndefined(vs.model)) {
                    return false;
                } else if (_.isArray(vs.model) && vs.model.length === 0) {
                    return false;
                } else if (_.isUndefined(vs.display) === false) {
                    return vs.display(vs.model);
                } else {
                    return true;
                }
            });
        }
    });

    // View renderer (all) - set view section dom.
    // @ctx     View rendering context.
    DocumentView.setRenderer({
        documentType : 'all',
        uiMode : 'all',
        task : function (ctx) {
            _.each(ctx.viewSections, function(vs) {
                vs.$dom = ctx.view.addSection(vs.name);
            });
        }
    });

    // View renderer (all) - set view section fieldset views.
    // @ctx     View rendering context.
    DocumentView.setRenderer({
        documentType : 'all',
        uiMode : 'all',
        task : function (ctx) {
            var viewSections,
                fieldSet,
                view,
                viewRenderMode = 'inline';

            // Filter view sections.
            viewSections = _.filter(ctx.viewSections, function (vs) {
                return _.has(vs, 'getFieldSet');
            });

            // Build views.
            _.each(viewSections, function (vs) {
                // ... format model.
                fieldSet = vs.getFieldSet(vs.model);
                fieldSet = _.reduce(fieldSet, function (fs, f) {
                    fs.push({
                        title : f[0],
                        expression : f[1]
                    });
                    return fs;
                }, []);

                // ... set render mode.
                if (_.has(vs, 'getFieldSetRenderMode')) {
                    viewRenderMode = vs.getFieldSetRenderMode();
                }

                // ... render view.
                view = new CIM.utils.views.FieldSetView({
                    fieldSet : {
                        model : vs.model,
                        fields : fieldSet
                    },
                    renderMode : viewRenderMode
                });
                view.render();

                // ... update dom.
                vs.$dom.append(view.$el.children());
            });
        }
    });

    // View renderer (all) - set view section name value views.
    // @ctx     View rendering context.
    DocumentView.setRenderer({
        documentType : 'all',
        uiMode : 'all',
        task : function (ctx) {
            var viewSections,
                view;

            // Filter view sections.
            viewSections = _.filter(ctx.viewSections, function (vs) {
                return _.has(vs, 'getNamedValueSet');
            });

            // Build views.
            _.each(viewSections, function (vs) {
                // ... render view.
                view = new CIM.utils.views.NamedValueSetView({
                    model : vs.getNamedValueSet(vs.model)
                });
                view.render();

                // ... update view dom.
                vs.$dom.append(view.$el.children());
            });
        }
    });

    // View renderer (all) - set view section name value views.
    // @ctx     View rendering context.
    DocumentView.setRenderer({
        documentType : 'all',
        uiMode : 'all',
        task : function (ctx) {
            var viewSections,
                view;

            // Filter view sections.
            viewSections = _.filter(ctx.viewSections, function (vs) {
                return _.has(vs, 'getNamedValueGroupSet');
            });

            // Build views.
            _.each(viewSections, function (vs) {
                // ... render view.
                view = new CIM.utils.views.NamedValueGroupSetView({
                    model : vs.getNamedValueGroupSet(vs.model)
                });
                view.render();

                // ... update dom.
                vs.$dom.append(view.$el.children());
            });
        }
    });

    // View renderer (tabs) - instantiate section tabs.
    // @ctx     View rendering context.
    DocumentView.setRenderer({
        documentType : 'all',
        uiMode : 'tabs',
        uiFramework : 'jq',
        task : function (ctx) {
            var tabset, tabsetView;

            // Create tabset.
            tabset = _(ctx.viewSections).reduce(function(tabs, vs) {
                tabs.push({
                    title : vs.title,
                    id : vs.$dom.attr('id')
                });
                return tabs;
            }, []);

            // Render tabset.
            tabsetView = new CIM.utils.views.TabsetView({
                $content : ctx.view.$document,
                $contentWrapper : ctx.view.$el,
                tabset : tabset
            });
            tabsetView.render();
        }
    });

}).call(this);



// --------------------------------------------------------
// jscim.viewer.views.core.viewPort - document view content display port.
// --------------------------------------------------------
(function() {
    // Module variables.
    var CIM = this.CIM,
        ViewportHeaderView,
        ViewportContentView,
        ViewportFooterView;

    // Viewer header view class.
    ViewportHeaderView = Backbone.View.extend({
        // Backbone : events.
        events: {
            "click .toolbar-button" : "_onToolbarButtonClicked"
        },

        // Backbone : constructor.
        initialize : function () {
            // Initialize dom.
            this.myToolbar = $jq(this.make("span", {
                "class" :"toolbar",
                "id" : "cimDocumentSetToolbar"
            }));
            this.myCaption = $jq(this.make("span", {
                "class" : "caption"
            }));

            // Wire dom.
            this.$el.append(this.myToolbar);
            this.$el.append(this.myCaption);

            // Hook events.
            CIM.events.on("viewer:documentSelected", this._onDocumentSelected, this);
        },

        // Backbone : destructor.
        destroy : function () {
            // Unhook events.
            CIM.events.off("viewer:documentSelected", this._onDocumentSelected);
        },

        // Backbone : render.
        render : function () {
            this._renderToolbar();
            this._renderJqueryUI();
        },

        // Renders toolbar.
        _renderToolbar : function () {
            var view = this, isFirst = true,
            buttonID, buttonAtts, button, buttonLabel, buttonText;

            // Set toolbar buttons.
            // TODO filter by renderable documents.
            _.each(this.options.documents.renderable, function ( document ) {
                // ... set attributes.
                buttonID = document.cimInfo.key + '-button';
                buttonAtts = {
                    id : buttonID,
                    "class" : "toolbar-button",
                    type : "radio",
                    name : "cimDocumentSetToolbar"
                };
                if (isFirst === true) {
                    _.extend(buttonAtts, {
                        checked : 'checked'
                    });
                    isFirst = false;
                }

                // ... create button + label.
                button = $jq(view.make("input", buttonAtts));
                buttonText = CIM.utils.schemas.getDocumentDisplayName(document);
                buttonLabel = view.make("label",
                                        { "for" : buttonID },
                                        buttonText);

                // ... update dom.
                view.myToolbar.append(button);
                view.myToolbar.append(buttonLabel);
            });
        },

        // Renders jquery-ui framework views.
        _renderJqueryUI : function () {
            this.$el.parent().addClass('ui-state-highlight ui-corner-all');
            this.$el.addClass('ui-corner-all');
            this.$('.caption').addClass('ui-widget-header ui-corner-all');
            this.$('.toolbar')
                .buttonset()
                .find('label')
                    .css('width', '120px');
        },

        // Event handler fired whenever a toolbar button click event occurs.
        // @e     Toolbar click event handler.
        _onToolbarButtonClicked : function ( e ) {
            var documentKey, document;

            // Get document.
            documentKey = e.currentTarget.id.replace('-button', '')
            document = _.find(this.options.documents.renderable, function ( doc ) {
               return doc.cimInfo.key === documentKey;
            });

            // Trigger event.
            if (_.isUndefined(document) === false) {
                CIM.events.trigger("viewer:documentSelected",
                                   document,
                                   this.options.documents.all);
            }
        },

        // Event handler fired whenever a document is selected.
        // @document        Document being selected.
        _onDocumentSelected : function ( document ) {
            this.myCaption.text(document.cimDisplayTitle);
        }
    });

    // Viewer content view class.
    ViewportContentView = Backbone.View.extend({
        // Backbone : constructor.
        initialize : function () {
            // Initialize work variables.
            this._currentDocument = undefined;
            this._documentViews = {};

            // Hook events.
            CIM.events.on("viewer:documentSelected", this._onDocumentSelected, this);
        },

        // Backbone : destructor.
        destroy : function () {
            // Unhook events.
            CIM.events.off("viewer:documentSelected", this._onDocumentSelected);
        },

        // Backbone : render.
        render : function () {
            this._renderJqueryUI();
        },

        // Renders jquery-ui framework views.
        _renderJqueryUI : function () {
            this.$el.parent().addClass('ui-corner-all');
        },

        // Event handler fired whenever a document is selected.
        // @document        Document being selected.
        _onDocumentSelected : function ( document ) {
            // Escape if loading null document.
            if (_.isUndefined(document)) {
                return;
            }

            // Escape if re-loading current document.
            if (_.isUndefined(this._currentDocument) === false &&
                this._currentDocument.cimInfo.key === document.cimInfo.key) {
                return;
            }

            // Create new (if necessary).
            if (_.has(this._documentViews, document.cimInfo.key) === false) {
                this._createDocumentView(document);
            }

            // Hide old.
            if (_.isUndefined(this._currentDocument) === false) {
                this._documentViews[this._currentDocument.cimInfo.key].$el.hide();
            }

            // Display new.
            this._documentViews[document.cimInfo.key].$el.show();

            // Update current document.
            this._currentDocument = document;
        },

        // Creates a new document view.
        // @document        Document being selected.
        _createDocumentView : function ( document ) {
            var view, viewOptions;
            
            // Instantiate.
            viewOptions = {
                document : document,
                documentType : document.cimInfo.typeKey,
                documentSet : this.options.documents.all
            };
            view = new CIM.viewer.views.DocumentView(viewOptions);

            // Cache.
            this._documentViews[document.cimInfo.key] = view;

            // Render.
            view.render();

            // Update dom.
            this.$el.append(view.$el);
        }
    });

    // Viewer footer view class.
    ViewportFooterView = Backbone.View.extend({
        // Backbone : constructor.
        initialize : function () {
            var inner, me = this, el;

            // Initialize dom.
            this.myDocumentCount = $jq(this.make("span", {
                "class" :"document-count"
            }));
            this.myDocumentCountLabel = $jq(this.make("span", {
                "class" :"label"
            }, "Documents : "));
            this.myDocumentCountText = $jq(this.make("span", {
                "class" :"text"
            }, this.options.documents.renderable.length));
            this.myDocumentSummary = $jq(this.make("span", {
                "class" : "document-summary"
            }));
            this.myDocumentSummaryLabel = $jq(this.make("span", {
                "class" :"label"
            }, "Document : "));
            this.myDocumentSummaryText = $jq(this.make("span", {
                "class" :"text"
            }));

            // Wire dom.
            this.$el.append(this.myDocumentCount);
            this.myDocumentCount.append(this.myDocumentCountLabel);
            this.myDocumentCount.append(this.myDocumentCountText);
            this.$el.append(this.myDocumentSummary);
            this.myDocumentSummary.append(this.myDocumentSummaryLabel);
            this.myDocumentSummary.append(this.myDocumentSummaryText);

            // Hook events.
            CIM.events.on("viewer:documentSelected", this._onDocumentSelected, this);
        },

        // Backbone : destructor.
        destroy : function () {
            // Unhook events.
            CIM.events.off("viewer:documentSelected", this._onDocumentSelected);
        },

        // Backbone : render.
        render : function () {
            this._renderJqueryUI();
        },

        // Renders jquery-ui framework views.
        _renderJqueryUI : function () {
            this.$el.parent().addClass('ui-state-highlight ui-corner-all');
            this.$el.addClass('ui-corner-all');
        },
        
        // Event handler fired whenever a document is selected.
        // @document        Document being selected.
        _onDocumentSelected : function ( document ) {
            this.myDocumentSummaryText.text(document.cimDisplayTitle);
        }
    });

    // Viewer container view class.
    CIM.viewer.views.DocumentViewport = Backbone.View.extend({
        // Backbone : view attributes.
        className : "cim-viewer",

        // Backbone : donstructor.
        initialize : function () {
            // Initialise set of sub-views.
            this._subviews = [];
            if (this.options.documents.renderable.length > 1) {
                this._subviews.push(new ViewportHeaderView({
                    el: this.makePanel('header'),
                    documents : this.options.documents
                }));
            }
            this._subviews.push(new ViewportContentView({
                el: this.makePanel('content'),
                documents : this.options.documents
            }));
            this._subviews.push(new ViewportFooterView({
                el: this.makePanel('footer'),
                documents : this.options.documents
            }));
        },
        
        // Backbone : destructor.
        destroy : function () {
            // Destroy sub-views.
            _.each(this._subviews, function(subview) {
                subview.destroy();
            });

            // Unhook events.
            CIM.events.off("viewer:documentSelected", this.onDocumentSelected);
        },

        // Backbone : render.
        render : function () {
            // Render sub-views.
            _.each(this._subviews, function(subview) {
                subview.render();
            });
        },

        // Helper function : Creates a sub-element.
        $make : function (tag, p1, p2) {
            var atts = {}, text;
            
            if (_.isObject(p1) === true) {
                _.extend(atts, p1);
                text = p2;
            } else {
                if (_.isString(p1) === true) {
                    _.extend(atts, {"class" : p1});
                }
                if (_.isString(p2) === true) {
                    _.extend(atts, {id : p2});
                }
            }

            return $jq(this.make(tag, atts, text));
        },

        // Helper function : Creates a viewer sub-panel.
        makePanel : function(panelClass) {
            var outer, panel;

            outer = this.$make("div", panelClass + '-outer');
            panel = this.$make("div", panelClass);
            this.$el.append(outer);
            outer.append(panel);
            
            return panel;
        }
    });

}).call(this);


// --------------------------------------------------------
// jscim.viewer.views.v1.5.activity.numericalExperiment - document view.
// --------------------------------------------------------
(function() {
    // Module variables.
    var CIM = this.cim,
        DocumentView = CIM.viewer.views.DocumentView,
        DOC_TYPE = '1.5-activity-numericalExperiment',
        applyDefaults;

    // TODO - move this functionailty into options.
    // Set function to apply default rendering options over user defined options.
    // @userOpts		User defined rendering options.
    // @defaultOpts		Default rendering options.
    applyDefaults = function (userOpts, defaultOpts) {
        _.defaults(userOpts, defaultOpts);
        _.defaults(userOpts.general, defaultOpts.general);
        _.defaults(userOpts.general.dialog, defaultOpts.general.dialog);
        _.defaults(userOpts.sections, defaultOpts.sections);
        _.defaults(userOpts.sections.overview, defaultOpts.sections.overview);
        _.defaults(userOpts.sections.cimInfo, defaultOpts.sections.cimInfo);
    };

    // View template metadata.
    DocumentView.setMetadata({
        documentType : DOC_TYPE,
        create : function () {
            return {
                overview : {
                    name : 'overview',
                    title : 'Overview',
                    titleLong : 'Overview',
                    getFieldSet : function (model) {
                        return [
                            ['Project', 'cimInfo.project'],
                            ['Short Name', 'shortName'],
                            ['Long Name', 'longName'],
                            ['Description', 'description'],
                            ['Rationale', 'rationales']
                        ]
                    },
                    filterModel : function(experiment) {
                        return experiment;
                    }
                },
                requirements : {
                    name : 'requirements',
                    title : 'Requirements',
                    titleLong : 'Requirements',
                    getFieldSet : function (model) {
                        return [
                            ['ID', 'id'],
                            ['Name', 'name'],
                            ['Description', 'description'],
                        ]
                    },
                    filterModel : function(experiment) {
                        return experiment.requirements;
                    }
                },
                cimInfo : {
                    name : 'cimInfo',
                    title : 'CIM Info',
                    titleLong : 'CIM Information',
                    getFieldSet : function (model) {
                        return [
                            ['Project', 'project'],
                            ['Source', 'source'],
                            ['ID', 'id'],
                            ['Version', 'version'],
                            ['Creation Date', 'createDate'],
                            ['Schema', 'typeInfo.schema'],
                            ['Package', 'typeInfo.package'],
                            ['Type', 'typeInfo.type'],
                        ]
                    },
                    filterModel : function(experiment) {
                        return experiment.cimInfo;
                    }
                }
            };
        }
    });

    // View options.
    DocumentView.setOptions({
        documentType : DOC_TYPE,
        renderingOrder : 2,
        defaults : {
            // Display mode.
            mode : 'tabs',                  // one of: tabs | inline

            // Sections.
            sections : [
                {
                    name : 'overview',
                    display : true,
                    mode : 'inline'         // one of: inline
                },
                {
                    name : 'requirements',
                    display : true,
                    mode : 'inline'         // one of: inline
                },
                {
                    name : 'cimInfo',
                    display : true,
                    mode : 'inline'         // one of: inline
                }
            ]
        }
    });

}).call(this);


// --------------------------------------------------------
// jscim.viewer.views.v1.5.activity.simulationRun - document view.
// --------------------------------------------------------
(function() {
    // Module variables.
    var CIM = this.cim,
        DocumentView = CIM.viewer.views.DocumentView,
        DOC_TYPE = '1.5-activity-simulationRun';

    // View metadata (used for templating purposes).
    DocumentView.setMetadata({
        documentType : DOC_TYPE,
        create : function () {
            return {
                overview : {
                    name : 'overview',
                    title : 'Overview',
                    titleLong : 'Overview',
                    getFieldSet : function (model) {
                        return [
                            ['Project', 'cimInfo.project'],
                            ['Short Name', 'shortName'],
                            ['Long Name', 'longName'],
                            ['Release Date', 'releaseDate'],
                            ['Description', 'description']
                        ]
                    },
                    filterModel : function(model) {
                        return model;
                    }
                },
                parties : {
                    name : 'parties',
                    title : 'Parties',
                    titleLong : 'Responsible Parties',
                    getFieldSet : function (model) {
                        return [
                            ['Role', 'role'],
                            ['Person', 'individual_name'],
                            ['Organisation', 'organisation_name'],
                            ['Address', 'contact_info.address'],
                            ['Email', 'contact_info.email'],
                            ['URL', 'contact_info.url'],
                        ]
                    },
                    filterModel : function(model) {
                        return model.responsibleParties;
                    }
                },
                citations : {
                    name : 'citations',
                    title : 'Citations',
                    titleLong : 'Citations',
                    getFieldSet : function (model) {
                        return [
                            ['Title', 'title'],
                            ['Type', 'type'],
                            ['Location', 'location'],
                            ['Collective Title', 'collectiveTitle'],
                        ]
                    },
                    filterModel : function(model) {
                        return model.citations;
                    }
                },
                components : {
                    name : 'components',
                    title : 'Components',
                    titleLong : 'Components (top-level)',
                    getFieldSet : function (model) {
                        return [
                            ['Short Name', 'shortName'],
                            //                    ['Type', 'type'],
                            ['Description', 'description']
                        ]
                    },
                    filterModel : function(model) {
                        return model.childComponents;
                    }
                },
                cimInfo : {
                    name : 'cimInfo',
                    title : 'CIM Info',
                    titleLong : 'CIM Information',
                    getFieldSet : function (model) {
                        return [
                            ['Project', 'project'],
                            ['Source', 'source'],
                            ['ID', 'id'],
                            ['Version', 'version'],
                            ['Creation Date', 'createDate'],
                            ['Schema', 'typeInfo.schema'],
                            ['Package', 'typeInfo.package'],
                            ['Type', 'typeInfo.type'],
                        ]
                    },
                    filterModel : function(model) {
                        return model.cimInfo;
                    }
                }
            }
        }
    });

    // View options.
    DocumentView.setOptions({
        documentType : DOC_TYPE,
        renderingOrder : 1,
        defaults : {
            // Display mode.
            mode : 'tabs',                  // one of: tabs | inline

            // Sections.
            sections : [
                {
                    name : 'parties',
                    display : true,
                    mode : 'inline'         // one of: inline
                },
                {
                    name : 'cimInfo',
                    display : true,
                    mode : 'inline'         // one of: inline
                }
            ]
        }
    });

}).call(this);


// --------------------------------------------------------
// jscim.viewer.views.v1.5.activity.platform - document view.
// --------------------------------------------------------
(function() {
    // Module variables.
    var CIM = this.cim,
        DocumentView = CIM.viewer.views.DocumentView,
        DOC_TYPE = '1.5-activity-platform';

    // View metadata (used for templating purposes).
    DocumentView.setMetadata({
        documentType : DOC_TYPE,
        create : function () {
            return {
                overview : {
                    name : 'overview',
                    title : 'Overview',
                    titleLong : 'Overview',
                    getFieldSet : function (model) {
                        return [
                            ['Project', 'cimInfo.project'],
                            ['Short Name', 'shortName'],
                            ['Long Name', 'longName'],
                            ['Release Date', 'releaseDate'],
                            ['Description', 'description']
                        ]
                    },
                    filterModel : function(model) {
                        return model;
                    }
                },
                parties : {
                    name : 'parties',
                    title : 'Parties',
                    titleLong : 'Responsible Parties',
                    getFieldSet : function (model) {
                        return [
                            ['Role', 'role'],
                            ['Person', 'individual_name'],
                            ['Organisation', 'organisation_name'],
                            ['Address', 'contact_info.address'],
                            ['Email', 'contact_info.email'],
                            ['URL', 'contact_info.url'],
                        ]
                    },
                    filterModel : function(model) {
                        return model.responsibleParties;
                    }
                },
                citations : {
                    name : 'citations',
                    title : 'Citations',
                    titleLong : 'Citations',
                    getFieldSet : function (model) {
                        return [
                            ['Title', 'title'],
                            ['Type', 'type'],
                            ['Location', 'location'],
                            ['Collective Title', 'collectiveTitle'],
                        ]
                    },
                    filterModel : function(model) {
                        return model.citations;
                    }
                },
                components : {
                    name : 'components',
                    title : 'Components',
                    titleLong : 'Components (top-level)',
                    getFieldSet : function (model) {
                        return [
                            ['Short Name', 'shortName'],
                            //                    ['Type', 'type'],
                            ['Description', 'description']
                        ]
                    },
                    filterModel : function(model) {
                        return model.childComponents;
                    }
                },
                cimInfo : {
                    name : 'cimInfo',
                    title : 'CIM Info',
                    titleLong : 'CIM Information',
                    getFieldSet : function (model) {
                        return [
                            ['Project', 'project'],
                            ['Source', 'source'],
                            ['ID', 'id'],
                            ['Version', 'version'],
                            ['Creation Date', 'createDate'],
                            ['Schema', 'typeInfo.schema'],
                            ['Package', 'typeInfo.package'],
                            ['Type', 'typeInfo.type'],
                        ]
                    },
                    filterModel : function(model) {
                        return model.cimInfo;
                    }
                }
            }
        }
    });

    // View options.
    DocumentView.setOptions({
        documentType : DOC_TYPE,
        renderingOrder : 100,
        defaults : {
            // Display mode.
            mode : 'tabs',                  // one of: tabs | inline

            // Sections.
            sections : [
                {
                    name : 'cimInfo',
                    display : true,
                    mode : 'inline'         // one of: inline
                }
            ]
        }
    });

}).call(this);


// --------------------------------------------------------
// jscim.viewer.views.v1.5.grids.gridSpec - document view.
// --------------------------------------------------------
(function() {
    // Module variables.
    var CIM = this.cim,
        DocumentView = CIM.viewer.views.DocumentView,
        DOC_TYPE = '1.5-grids-gridSpec';

    // View metadata (used for templating purposes).
    DocumentView.setMetadata({
        documentType : DOC_TYPE,
        create : function () {
            return {
                overview : {
                    name : 'overview',
                    title : 'Overview',
                    titleLong : 'Overview',
                    getFieldSet : function (model) {
                        return [
                            ['Project', 'cimInfo.project'],
                            ['Short Name', 'shortName'],
                            ['Long Name', 'longName'],
                            ['Release Date', 'releaseDate'],
                            ['Description', 'description']
                        ]
                    },
                    filterModel : function(model) {
                        return model;
                    }
                },
                parties : {
                    name : 'parties',
                    title : 'Parties',
                    titleLong : 'Responsible Parties',
                    getFieldSet : function (model) {
                        return [
                            ['Role', 'role'],
                            ['Person', 'individual_name'],
                            ['Organisation', 'organisation_name'],
                            ['Address', 'contact_info.address'],
                            ['Email', 'contact_info.email'],
                            ['URL', 'contact_info.url'],
                        ]
                    },
                    filterModel : function(model) {
                        return model.responsibleParties;
                    }
                },
                citations : {
                    name : 'citations',
                    title : 'Citations',
                    titleLong : 'Citations',
                    getFieldSet : function (model) {
                        return [
                            ['Title', 'title'],
                            ['Type', 'type'],
                            ['Location', 'location'],
                            ['Collective Title', 'collectiveTitle'],
                        ]
                    },
                    filterModel : function(model) {
                        return model.citations;
                    }
                },
                components : {
                    name : 'components',
                    title : 'Components',
                    titleLong : 'Components (top-level)',
                    getFieldSet : function (model) {
                        return [
                            ['Short Name', 'shortName'],
                            //                    ['Type', 'type'],
                            ['Description', 'description']
                        ]
                    },
                    filterModel : function(model) {
                        return model.childComponents;
                    }
                },
                cimInfo : {
                    name : 'cimInfo',
                    title : 'CIM Info',
                    titleLong : 'CIM Information',
                    getFieldSet : function (model) {
                        return [
                            ['Project', 'project'],
                            ['Source', 'source'],
                            ['ID', 'id'],
                            ['Version', 'version'],
                            ['Creation Date', 'createDate'],
                            ['Schema', 'typeInfo.schema'],
                            ['Package', 'typeInfo.package'],
                            ['Type', 'typeInfo.type'],
                        ]
                    },
                    filterModel : function(model) {
                        return model.cimInfo;
                    }
                }
            }
        }
    });

    // View options.
    DocumentView.setOptions({
        documentType : DOC_TYPE,
        renderingOrder : 10,
        defaults : {
            // Display mode.
            mode : 'tabs',                  // one of: tabs | inline

            // Sections.
            sections : [
                {
                    name : 'cimInfo',
                    display : true,
                    mode : 'inline'         // one of: inline
                }
            ]
        }
    });

}).call(this);


// --------------------------------------------------------
// jscim.viewer.views.v1.5.software.modelComponent - document view.
// --------------------------------------------------------
(function() {
    // Module variables.
    var CIM = this.cim,
        DocumentView = CIM.viewer.views.DocumentView,
        DOC_TYPE = '1.5-software-modelComponent';

    // View metadata (used for templating purposes).
    DocumentView.setMetadata({
        documentType : DOC_TYPE,
        create : function () {
            return {
                overview : {
                    name : 'overview',
                    title : 'Overview',
                    titleLong : 'Overview',
                    getFieldSet : function (model) {
                        return [
                            ['Project', 'cimInfo.project'],
                            ['Short Name', 'shortName'],
                            ['Long Name', 'longName'],
                            ['Language', 'componentLanguage.name'],
                            ['Release Date', 'releaseDate'],
                            ['Description', 'description']
                        ]
                    }
                },
                parties : {
                    name : 'parties',
                    title : 'Parties',
                    titleLong : 'Responsible Parties',
                    getFieldSet : function (model) {
                        var result = [
                            ['Role', 'role'],
                            ['Person', 'individualName'],
                            ['Organisation', 'organisationName'],
                        ]
                        if (_.has(model, 'contactInfo')) {
                            result.push(['Address', 'contactInfo.address']);
                            result.push(['Email', 'contactInfo.email']);
                            result.push(['URL', 'contactInfo.url']);
                        }
                        return result;
                        
                    },
                    filterModel : function(model) {
                        return model.responsibleParties;
                    }
                },
                citations : {
                    name : 'citations',
                    title : 'Citations',
                    titleLong : 'Citations',
                    getFieldSet : function (model) {
                        return [
                            ['Title', 'title'],
                            ['Type', 'type'],
                            ['Location', 'location'],
                            ['Collective Title', 'collectiveTitle'],
                        ]
                    },
                    filterModel : function(model) {
                        return model.citations;
                    }
                },
                components : {
                    name : 'components',
                    title : 'Components',
                    titleLong : 'Components (top-level)',
                    getFieldSet : function (model) {
                        return [
                            ['Short Name', 'shortName'],
                            //                    ['Type', 'type'],
                            ['Description', 'description']
                        ]
                    },
                    filterModel : function(model) {
                        return model.childComponents;
                    }
                },
                scientificProperties : {
                    name : 'scientificProperties',
                    title : 'Scientific Props.',
                    titleLong : 'Properties',                    
                    getNamedValueGroupSet : function (sprops) {
                        var result = [],
                            general, other = [], group;

                        // Create general group.
                        general = {
                            title : 'General',
                            namedValueSet : []
                        }
                        result.push(general);

                        // Iterate scientific properties ...
                        _.each(sprops, function (sprop) {
                            // ... add to general group.
                            if (sprop.componentProperties.length == 0) {
                                general.namedValueSet.push({
                                    name : sprop.longName,
                                    value : sprop.value
                                });
                            // ... create new group.
                            } else {
                                group = {
                                    title : sprop.longName,
                                    namedValueSet : []
                                }
                                _.each(sprop.componentProperties, function (sp) {
                                    group.namedValueSet.push({
                                        name : sp.shortName,
                                        value : sp.value
                                    });
                                });
                                other.push(group);
                            }
                        });
                        result = result.concat(_.sortBy(other, 'title'));

                        return result;
                    },
                    filterModel : function(model) {
                        return model.scientificProperties;
                    }
                },
                cimInfo : {
                    name : 'cimInfo',
                    title : 'CIM Info',
                    titleLong : 'CIM Information',
                    getFieldSet : function (model) {
                        return [
                            ['Project', 'project'],
                            ['Source', 'source'],
                            ['ID', 'id'],
                            ['Version', 'version'],
                            ['Creation Date', 'createDate'],
                            ['Schema', 'typeInfo.schema'],
                            ['Package', 'typeInfo.package'],
                            ['Type', 'typeInfo.type'],
                        ]
                    },
                    filterModel : function(model) {
                        return model.cimInfo;
                    }
                }
            }
        }
    });

    // View options.
    DocumentView.setOptions({
        documentType : DOC_TYPE,
        renderingOrder : 1,
        defaults : {
            // Display mode.
            mode : 'tabs',                  // one of: tabs | inline

            // Sections.
            sections : [
                {
                    name : 'overview',
                    display : true,
                    mode : 'inline'         // one of: inline
                },
                {
                    name : 'parties',
                    display : true,
                    mode : 'inline'         // one of: inline | table
                },
                {
                    name : 'citations',
                    display : true,
                    mode : 'inline'         // one of: inline | table
                },
                {
                    name : 'components',
                    display : true,
                    mode : 'topInline'      // one of: inline | accordion | tabs | treeview | mindmap
                },
                {
                    name : 'scientificProperties',
                    display : true,
                    mode : 'topInline'      // one of: inline | accordion | tabs | treeview | mindmap
                },
                {
                    name : 'cimInfo',
                    display : true,
                    mode : 'inline'         // one of: inline
                }
            ]
        }
    });

    // View renderer (tabs) - instantiate section tabs.
    // @ctx     View rendering context.
    DocumentView.setRenderer({
        documentType : DOC_TYPE,
        uiMode : 'all',
        uiFramework : 'all',
        predicate : function (ctx) {
            return true;
        },
        task : function (ctx) {
            
        }
    });

}).call(this);


