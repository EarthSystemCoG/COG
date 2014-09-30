// ECMAScript 5 Strict Mode
"use strict";

// --------------------------------------------------------
// $jq :: JQuery nonconflict reference.
// See :: http://www.tvidesign.co.uk/blog/improve-your-jquery-25-excellent-tips.aspx#tip19
// --------------------------------------------------------
window.$ = window.$jq = jQuery.noConflict();

// --------------------------------------------------------
// cim :: CIM nonconflict reference.
// See :: http://www.tvidesign.co.uk/blog/improve-your-jquery-25-excellent-tips.aspx#tip19
// --------------------------------------------------------
if (window.cim === undefined) {
    window.cim = {};
}


// --------------------------------------------------------
// cim.viewer :: Renders views of cim instances.
// N.B. Declared in a functional closure so as not to pollute global namespace.
// --------------------------------------------------------
cim.viewer = (function() {
    // Event handler for document ready event.
    $jq(document).ready(function() {
        // Inject cim viewer dialog div.
        cim.viewer.HTML.appendHTMLDiv('body', 'cimViewerDialog', 'cim-viewer-dialog');
    });

    // Renders a view of a CIM instance based upon its type, name and view options.
    // @project     Project with which CIM metadata is associated.
    // @cim_type    CIM instance type being rendered.
    // @name        Name  of CIM instance being rendered.
    // @options     Rendering options.
    var renderFromName = function(project, cim_type, name, options) {
        var target;         // Rendering target.
        var targets;        // Set of rendering targets.

        // Set of supported targets.
        targets = {
            'MODEL' : {
                renderFn : cim.viewer.renderer.forModel.render,
                serviceFn : cim.servicesProxy.query.getModelByName
            },
            'DATAOBJECT' : {
                renderFn : cim.viewer.renderer.forDataObject.render,
                serviceFn : cim.servicesProxy.query.getDataObjectByAcronym
            },
            'EXPERIMENT' : {
                renderFn : cim.viewer.renderer.forExperiment.render,
                serviceFn : cim.servicesProxy.query.getExperimentByName
            },
            'SIMULATION' : {
                renderFn : cim.viewer.renderer.forSimulation.render,
                serviceFn : cim.servicesProxy.query.getSimulationByName
            }           
        };

        // Assign rendering target.
        target = targets[cim_type.toUpperCase()];

        // Callback invoked when service operation completes.
        var serviceCallback = function(cim) {
            target.renderFn(cim, options);
        };

        // Invoke service operation (invoking callback on success).
        target.serviceFn(project, name, serviceCallback);
    };

    // Renders a view of a CIM instance based upon its id/version and view options.
    // @id          ID of CIM instance being rendered.
    // @version     Version of CIM instance being rendered.
    // @options     Rendering options.
    var renderFromID = function(id, version, options) {
        alert('TODO - render by ID');
    };


    // Return object pointer wrapped in functional closure.
    return {
        // Renders a view of a CIM instance based upon its type, name and view options.
        renderFromName : renderFromName,

        // Renders a view of a CIM instance based upon its id/version and view options.
        renderFromID : renderFromID,
        
        // Default view options.
        viewOptions : {
            // Default view options for CIM model rendering.
            forModel : undefined,

            // Default view options for CIM data object rendering.
            forDataObject : undefined,

            // Default view options for CIM experiment rendering.
            forExperiment : undefined,

            // Default view options for CIM simulation rendering.
            forSimulation : undefined
        }
    };
}());


// --------------------------------------------------------
// cim.viewer.dialog :: Helper encapulating displaying views as a modal dialog.
// N.B. Declared in a functional closure so as not to pollute global namespace.
// --------------------------------------------------------
cim.viewer.dialog = (function() {
    // Returns dialog title based upon CIM instance being rendered.
    // @ctx         Rendering context.
    var getTitle = function(ctx) {
        var title = 'CIM ';
        title += ctx.cim.cimInfo.schema;
        title += ' - ';
        title += ctx.cim.cimInfo.type;
        title += ' : ';
        title += ctx.cim.shortName;
        return title;
    };

    // Opens dialog.
    // @ctx         Rendering context.
    var open = function(ctx) {
        // Dialog options.
        var options = ctx.options.dialog;

        // Destroy previous.
        $jq('#cimViewerDialog').dialog("destroy");

        // Create new.
        $jq('#cimViewerDialog').dialog({
            bgiframe: false,
            autoOpen: false,
            maxHeight : options.maxHeight,
            width: options.width,
            position: ['center', 80],
            modal: true,
            resizable: false,
            open: function(event, ui) {
                $(this).css({'max-height': options.maxHeight, 'overflow-y': 'auto'});
            }
        });

        // Set title and open.
        $jq('#cimViewerDialog').dialog('option', 'title', getTitle(ctx));
        $jq('#cimViewerDialog').dialog('open');
    };

    // Return object pointer wrapped in functional closure.
    return {
        open : open
    };
}());


// --------------------------------------------------------
// cim.viewer.HTML :: Helper encapulating html injection functions.
// N.B. Declared in a functional closure so as not to pollute global namespace.
// --------------------------------------------------------
cim.viewer.HTML = (function() {

    // Appends an html tabs collection to passed container dom ID.
    // @parentID     ID of parent html element.
    // @tabsID       ID of tabs collection div.
    var appendHTMLTabs = function(parentID, tabsID) {
        var tabs = '<div id="{0}"><ul></ul></div>'.replace('{0}', tabsID);
        $jq("#" + parentID).append(tabs);
        return $jq('#{0} ul'.replace('{0}', tabsID));
    };

    // Appends an html tab to passed collection.
    // @tabs        Tab collection.
    // @tabInfo     Info regarding new tab to be appended to dom.
    var appendHTMLTab = function(tabs, tabInfo) {
        var tab = '<li><a href="#{0}">{1}</a></li>'
            .replace('{0}', tabInfo.domID)
            .replace('{1}', tabInfo.title);
        tabs.append(tab);
    };

    // Appends an html div to passed container.
    // @parentID     ID of parent html element.
    // @title        Title of accordion to appended to dom.
    var appendHTMLAccordion = function(parentID, title) {
        var accordion = '<h3><a href="#">{0}</a></h3>'.replace('{0}', title);
        var $div;

        // Append div.
        $jq("#" + parentID).append(accordion);

        return $div;
    };

    // Prepends an html div to passed container.
    // @parentID     ID of parent html element.
    // @title        Title of accordion to appended to dom.
    var prependHTMLAccordion = function(parentID, title) {
        var accordion = '<h3><a href="#">{0}</a></h3>'.replace('{0}', title);
        $jq("#" + parentID).before(accordion);
    };

    // Appends an html div to passed container.
    // @parentID     ID of parent html element.
    // @divID        ID of div to be appended to dom.
    // @divClass     Class of div to be appended to dom.
    // @divText      Text to be inserted into div.
    var appendHTMLDiv = function(parentID, divID, divClass, divText) {
        var div = '<div id="{0}"></div>'.replace('{0}', divID);
        var $div;

        // Append div.
        if (parentID === 'body') {
            $jq('body').append(div);
        } else {
            $jq("#" + parentID).append(div);
        }

        // Set div class.
        $div = $jq('#{0}'.replace('{0}', divID));
        if (divClass !== undefined) {
            $div.addClass(divClass);
        }

        // Set div text.
        if (divText !== undefined) {
            $div.text(divText);
        }

        return $div;
    };

    // Prepends an html div to passed container.
    // @parentID     ID of parent html element.
    // @divID        ID of div to be appended to dom.
    // @divClass     Class of div to be appended to dom.
    // @divText      Text to be inserted into div.
    var prependHTMLDiv = function(parentID, divID, divClass, divText) {
        var div = '<div id="{0}"></div>'.replace('{0}', divID);
        var $div;

        // Prepend div.
        if (parentID === 'body') {
            $jq('body').prepend(div);
        } else {
            $jq("#" + parentID).prepend(div);
        }

        // Set div class.
        $div = $jq('#{0}'.replace('{0}', divID));
        if (divClass !== undefined) {
            $div.addClass(divClass);
        }

        // Set div text.
        if (divText !== undefined) {
            $div.text(divText);
        }

        return $div;
    };

    // Returns an html snippet based upon a template field.
    // @field       An array of information: [ title, name ].
    var getHTMLForField = function(field) {
        return "\n\
            <div class='cim-row'>\n\
                <div class='cim-cell-label'>\n\
                    <span title='{title}'>{title}</span>\n\
                </div>\n\
                <div class='cim-cell-input'>\n\
                    <span title='<%= {name} %>'><%= {name} %></span>\n\
                </div>\n\
            </div>"
            .replace(/{title}/g, field[0])
            .replace(/{name}/g, field[1]);
    };

    // Returns an html snippet based upon a set of template fields.
    // @fields  Set of template fields.
    var getHTMLForFields = function (fields) {
        return _(fields).reduce(function(template, field){
            return template + getHTMLForField(field);
        }, '');
    };

    // Returns an html snippet based upon a template field group.
    // @fields  Set of template fields.
    var getHTMLForFieldGroup = function(fields) {
        return "\n\
        <div class='cim-row-group{suffix} ui-corner-all'>\n\
            {rows}\n\
        </div>"
        .replace(/{rows}/g, getHTMLForFields(fields))
        .replace('{suffix}', '');
    };

    // Returns an html snippet based upon injecting data into a template.
    // @data                JSON object form which data will be injected into template.
    // @view                View information (includes set of associated template fields).
    // @templateFactory     Factory method for creating html template to be injected with data.
    var getHTMLFromTemplate = function(data, view, templateFactory){
        var html = "";      // HTML to be rendered.
        var template;       // HTML template to be populated.

        // Create template (using underscore).
        template = templateFactory(view.fields);
        template = _.template(template);

        // Generate html (with help of underscore template engine):
        if (_.isArray(data)) {
            _(data).each(function (item) {
                html = html + template(item);
            });
        } else {
            html = html + template(data);
        }

        return html;
    };

    // Injects html into view by generating html from a json parsed template.
    // @cim                 CIM instance as a JSON object form which data will be injected into template.
    // @view                View information.
    // @templateFactory     Method to create template to be injected with data.
    var injectHTML = function(cim, view, templateFactory) {
        var data = view.getData(cim);
        var html = getHTMLFromTemplate(data, view, templateFactory);
        $('#' + view.domID).html(html);
    };

    // Return object pointer wrapped in functional closure.
    return {
        // Appends an html tabs collection to passed container dom ID.
        appendHTMLTabs : appendHTMLTabs,

        // Appends an html tab to passed collection.
        appendHTMLTab : appendHTMLTab,

        // Appends an html div to passed container.
        appendHTMLDiv : appendHTMLDiv,

        // Prepends an html div to passed container.
        prependHTMLDiv : prependHTMLDiv,

        // Appends an html accordion header to passed container.
        appendHTMLAccordion : appendHTMLAccordion,

        // Prepends an html accordion header to passed container.
        prependHTMLAccordion : prependHTMLAccordion,

        // Returns an html snippet based upon a template field.
        getHTMLForField : getHTMLForField,

        // Returns an html snippet based upon a set of template fields.
        getHTMLForFields : getHTMLForFields,

        // Returns an html snippet based upon a template field group.
        getHTMLForFieldGroup : getHTMLForFieldGroup,

        // Returns an html snippet based upon injecting data into a template.
        getHTMLFromTemplate : getHTMLFromTemplate,

        // Injects html into view by generating html from a json parsed template.
        injectHTML : injectHTML
    };
}());


// --------------------------------------------------------
// cim.viewer.metadata :: Helper encapulating view rendering metadata.
// N.B. Declared in a functional closure so as not to pollute global namespace.
// --------------------------------------------------------
cim.viewer.metadata = (function() {
    // Model view metadata.
    var forModel = {
        info : {
            domID : 'cimViewerForModel',
            dialogID : 'cimDialogForModel'
        },
        getVisibleSections : function(options) {
            var all = [
                this.sections.overview,
                this.sections.parties,
                this.sections.citations,
                this.sections.components,
                this.sections.cimInfo
            ];
            return all;
        },
        sections : {
            overview : {
                title : 'Overview',
                titleLong : 'Overview',
                domID : 'cimModelOverview',
                fields : [
                    ['Short Name', 'shortName'],
                    ['Long Name', 'longName'],
                    ['Description', 'description']
                ],
                getData : function(model) {
                    return model;
                }
            },
            parties : {
                title : 'Parties',
                titleLong : 'Responsible Parties',
                domID : 'cimModelParties',
                fields : [
                    ['Name', 'name'],
                    ['Role', 'role'],
                    ['Address', 'address'],
                    ['Email', 'email']
                ],
                getData : function(model) {
                    return model.parties;
                }
            },
            citations : {
                title : 'Citations',
                titleLong : 'Citations',
                domID : 'cimModelCitations',
                fields : [
                    ['Title', 'title'],
                    ['Type', 'type'],
                    ['Reference', 'reference'],
                    ['Location', 'location']
                ],
                getData : function(model) {
                    return model.citations;
                }
            },
            components : {
                title : 'Components',
                titleLong : 'Components (top-level)',
                domID : 'cimModelComponents',
                fields : [
                    ['Short Name', 'shortName'],
                    ['Type', 'type'],
                    ['Description', 'description']
                ],
                getData : function(model) {
                    return model.components;
                }
            },
            cimInfo : {
                title : 'CIM Info',
                titleLong : 'CIM Information',
                domID : 'cimModelCIM',
                fields : [
                    ['Schema', 'schema'],
                    ['ID', 'id'],
                    ['Version', 'version'],
                    ['Creation Date', 'createDate'],
                    ['Source', 'source']
                ],
                getData : function(model) {
                    return model.cimInfo;
                }
            }
        }
    };

    // Data object view metadata.
    var forDataObject = {
        info : {
            domID : 'cimViewerForDataObject',
            dialogID : 'cimDialogForDataObject'
        }
    };

    // Experiment view metadata.
    var forExperiment = {
        info : {
            domID : 'cimViewerForExperiment',
            dialogID : 'cimDialogForExperiment'
        }
    };


    // Simulation view metadata.
    var forSimulation = {
        info : {
            domID : 'cimViewerForSimulation',
            dialogID : 'cimDialogForSimulation'
        }
    };

    // Return object pointer wrapped in functional closure.
    return {
        // Model view metadata.
        forModel : forModel,

        // Data object view metadata.
        forDataObject : forDataObject,

        // Experiment view metadata.
        forExperiment : forExperiment,

        // Simulation view metadata.
        forSimulation : forSimulation
    };
}());


// --------------------------------------------------------
// cim.viewer.options :: Helper encapulating view rendering options.
// N.B. Declared in a functional closure so as not to pollute global namespace.
// --------------------------------------------------------
cim.viewer.options = (function() {
    // View options for CIM model rendering.
    var forModel = {
        // Set of default options.
        defaults : {
            mode : 'tabs',          // one of: tabs | inline
            dialog : {
                display : true,
                maxHeight : 800,
                width : 900
            },
            sections : {
                overview : {
                    display : true,
                    mode : 'inline'     // one of: inline
                },
                parties : {
                    display : true,
                    mode : 'inline'     // one of: inline | table
                },
                citations : {
                    display : true,
                    mode : 'inline'     // one of: inline | table
                },
                components : {
                    display : true,
                    mode : 'topInline'     // one of: inline | accordion | tabs | treeview | mindmap
                },
                cimInfo : {
                    display : true,
                    mode : 'inline'     // one of: inline
                }
            }
        },

        // Parses options to guarantee their validity.
        parse : function(options) {
            var defaults = forModel.defaults;
            if (options === undefined) {
                options = defaults;
            } else {
                if (options.mode === undefined) {
                    options.mode = defaults.mode;
                }
                if (options.dialog === undefined) {
                    options.dialog = defaults.dialog;
                } else {
                    if (options.dialog.display === undefined) {
                        options.dialog.display = defaults.dialog.display;
                    }
                    if (options.dialog.maxHeight === undefined) {
                        options.dialog.maxHeight = defaults.dialog.maxHeight;
                    }
                    if (options.dialog.width === undefined) {
                        options.dialog.width = defaults.dialog.width;
                    }
                }
                if (options.sections === undefined) {
                    options.sections = defaults.sections;
                } else {
                    if (options.sections.overview === undefined) {
                        options.sections.overview = defaults.sections.overview;
                    } else {
                        if (options.sections.overview.display === undefined) {
                            options.sections.overview.display = defaults.sections.overview.display;
                        }
                        if (options.sections.overview.mode === undefined) {
                            options.sections.overview.mode = defaults.sections.overview.mode;
                        }
                    }
                    if (options.sections.parties === undefined) {
                        options.sections.parties = defaults.sections.parties;
                    } else {
                        if (options.sections.parties.display === undefined) {
                            options.sections.parties.display = defaults.sections.parties.display;
                        }
                        if (options.sections.parties.mode === undefined) {
                            options.sections.parties.mode = defaults.sections.parties.mode;
                        }
                    }
                    if (options.sections.citations === undefined) {
                        options.sections.citations = defaults.sections.citations;
                    } else {
                        if (options.sections.citations.display === undefined) {
                            options.sections.citations.display = defaults.sections.citations.display;
                        }
                        if (options.sections.citations.mode === undefined) {
                            options.sections.citations.mode = defaults.sections.citations.mode;
                        }
                    }
                    if (options.sections.components === undefined) {
                        options.sections.components = defaults.sections.components;
                    } else {
                        if (options.sections.components.display === undefined) {
                            options.sections.components.display = defaults.sections.components.display;
                        }
                        if (options.sections.components.mode === undefined) {
                            options.sections.components.mode = defaults.sections.components.mode;
                        }
                    }
                    if (options.sections.cimInfo === undefined) {
                        options.sections.cimInfo = defaults.sections.cimInfo;
                    } else {
                        if (options.sections.cimInfo.display === undefined) {
                            options.sections.cimInfo.display = defaults.sections.cimInfo.display;
                        }
                        if (options.sections.cimInfo.mode === undefined) {
                            options.sections.cimInfo.mode = defaults.sections.cimInfo.mode;
                        }
                    }
                }
            }
        }
    };

    // View options for CIM data object rendering.
    var forDataObject = {
        defaults : {
            // TODO
        },

        // Parses options to guarantee their validity.
        parse : function(options) {
            var defaults = forDataObject.defaults;
            if (options === undefined) {
                options = defaults;
            } else {
                // TODO
            }
        }
    };

    // View options for CIM experiment rendering.
    var forExperiment = {
        defaults : {
            // TODO
        },

        // Parses options to guarantee their validity.
        parse : function(options) {
            var defaults = forExperiment.defaults;
            if (options === undefined) {
                options = defaults;
            } else {
                // TODO
            }
        }
    };

    // View options for CIM simulation rendering.
    var forSimulation = {
        defaults : {
            // TODO
        },

        // Parses options to guarantee their validity.
        parse : function(options) {
            var defaults = forSimulation.defaults;
            if (options === undefined) {
                options = defaults;
            } else {
                // TODO
            }
        }
    };

    // Return object pointer wrapped in functional closure.
    return {
        // Default view options for CIM model rendering.
        forModel : forModel,

        // Default view options for CIM data object rendering.
        forDataObject : forDataObject,

        // Default view options for CIM experiment rendering.
        forExperiment : forExperiment,

        // Default view options for CIM simulation rendering.
        forSimulation : forSimulation
    };
}());
