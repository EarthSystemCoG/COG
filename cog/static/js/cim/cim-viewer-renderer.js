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
// cim.viewer.renderer :: Helper object encapsulating view rendering.
// N.B. Declared in a functional closure so as not to pollute global namespace.
// --------------------------------------------------------
cim.viewer.renderer = {};

// --------------------------------------------------------
// cim.viewer.rendererForModel :: CIM viewer helper object that performs CIM model view rendering.
// N.B. Declared in a functional closure so as not to pollute global namespace.
// --------------------------------------------------------
cim.viewer.renderer.forModel = (function() {
    // Associated metadata used to generate view html.
    var myMetadata = cim.viewer.metadata.forModel;

    // Associated view options.
    var myOptions = cim.viewer.options.forModel;

    // Returns set of model sections to be rendered.
    // @options     Rendering options.
    var getSectionsForRendering = function(options) {
        var result = [];
        if (options.sections.overview.display === true) {
            result.push(myMetadata.sections.overview);
        }
        if (options.sections.parties.display === true) {
            result.push(myMetadata.sections.parties);
        }
        if (options.sections.citations.display === true) {
            result.push(myMetadata.sections.citations);
        }
        if (options.sections.components.display === true) {
            result.push(myMetadata.sections.components);
        }
        if (options.sections.cimInfo.display === true) {
            result.push(myMetadata.sections.cimInfo);
        }
        return result;
    }

    // Rendering task - destory/create viewer container divs.
    // @ctx         Rendering context.
    var doRenderTask1 = function(ctx) {
        var injectDiv = cim.viewer.HTML.appendHTMLDiv;  // Div injection function.
        var injectContent = cim.viewer.HTML.getHTMLForFieldGroup;  // Section content injection function.

        // Destroy precious rendering.
        $jq('#cimModelViewer').remove();

        // Inject viewer container divs.
        injectDiv = cim.viewer.HTML.appendHTMLDiv;
        injectDiv('cimViewerDialog', 'cimModelViewer', 'cim-model-viewer');
        injectDiv('cimModelViewer', 'cimModel', 'cim-model');

        // Inject section content.
        _.each(ctx.sections, function(section) {
            injectDiv('cimModel', section.domID);
            $jq('#' + section.domID).addClass('cim-model-section');
            cim.viewer.HTML.injectHTML(ctx.cim, section, injectContent);
        });
    };

    // Rendering task - inject tabs.
    // @ctx         Rendering context.
    var doRenderTask2 = function(ctx) {
        // Inject tabs container div.
        var $tabs = cim.viewer.HTML.appendHTMLTabs('cimModelViewer', 'cimModelViewTabs');

        // Setup tabs.
        _.each(ctx.sections, function(sectionInfo) {
            cim.viewer.HTML.appendHTMLTab($tabs, sectionInfo);
        });

        // Move standard view into tabs container.
        $jq('#cimModel').appendTo('#cimModelViewTabs')

        // Instantiate JQuery tab.
        $jq('#cimModelViewTabs').tabs({
            fx: {opacity : 'toggle'}
        });

        // Style JQuery tab.
        $jq("#cimModelViewTabs ul li a").css({
            'width' : '110px',
            'text-align' : 'center'
        });
    };

    // Rendering task - inject inline section headers.
    // @ctx         Rendering context.
    var doRenderTask3 = function(ctx) {
        var renderFn;      // Rendering function to apply.

        // Inject html for each section.
        renderFn = cim.viewer.HTML.prependHTMLDiv;
        _.each(ctx.sections, function(section) {
            renderFn(section.domID,
                     section.domID + 'Header',
                     'cim-section-header ui-state-highlight ui-corner-all',
                     section.titleLong);
        });
    };

    // Rendering task - inject accordion divs.
    // @ctx         Rendering context.
    var doRenderTask4 = function(ctx) {
        var renderFn;      // Rendering function to apply.

        // Inject accordion class.
        $jq('#cimModel').addClass('cim-viewer-accordion');

        // Inject accordion header elements.
        renderFn = cim.viewer.HTML.prependHTMLAccordion;
        _.each(ctx.sections, function(section) {
            renderFn(section.domID, section.title);
        });

        // Instantiate JQuery accordion.
        $jq('.cim-viewer-accordion').accordion({
            fillSpace: true
        });
    };

    // // Rendering task - display dialog.
    // @ctx         Rendering context.
    var doRenderTask5 = function(ctx) {
        if (ctx.options.dialog.display === true) {
            cim.viewer.dialog.open(ctx);
        }
    };

    // Renders CIM model instance based upon passed options.
    // @cim         JSON encoded CIM instance (model).
    // @options     Rendering options.
    var render = function(cim, options) {
        var ctx, taskMode, task;

        // Instantiate context.
        ctx = {
            cim : cim,
            options : options,
            sections : getSectionsForRendering(options),
            tasks : [
                [ 'all', doRenderTask1 ],
                [ 'tabs', doRenderTask2 ],
                [ 'inline', doRenderTask3 ],
                [ 'accordion', doRenderTask4 ],
                [ 'all', doRenderTask5 ]
            ]
        };

        // Parse options (guarantees they are valid).
        myOptions.parse(ctx.options);

        // Invoke tasks.
        _.each(ctx.tasks, function(taskInfo){
            taskMode = taskInfo[0];
            if (taskMode === 'all' || taskMode === options.mode) {
                task = taskInfo[1];
                task(ctx);
            }
        });
    };

    // Return rendering function.
    return {
        render : render
    };
}());


// --------------------------------------------------------
// cim.viewer.rendererForDataObject :: CIM view renderer that render cim data objects.
// N.B. Declared in a functional closure so as not to pollute global namespace.
// --------------------------------------------------------
cim.viewer.renderer.forDataObject = (function() {
    // Associated metadata used to generate view html.
    var myMetadata = cim.viewer.metadata.forDataObject;

    // Associated view options.
    var myOptions = cim.viewer.options.forDataObject;

    // Renders CIM data object instance based upon passed options.
    // @cim         JSON encoded CIM instance (data object).
    // @options     Rendering options.
    var render = function(cim, options) {
        // TODO
        alert('TODO - render data objects');
    };

    // Return rendering function.
    return {
        render : render
    };
}());


// --------------------------------------------------------
// cim.viewer.rendererForExperiment :: CIM view renderer that render cim experiments.
// N.B. Declared in a functional closure so as not to pollute global namespace.
// --------------------------------------------------------
cim.viewer.renderer.forExperiment = (function() {
    // Associated metadata used to generate view html.
    var myMetadata = cim.viewer.metadata.forExperiment;

    // Associated view options.
    var myOptions = cim.viewer.options.forExperiment;

    // Renders CIM experiment instance based upon passed options.
    // @cim         JSON encoded CIM instance (experiment).
    // @options     Rendering options.
    var render = function(cim, options) {
        // TODO
        alert('TODO - render experiments');
    };

    // Return rendering function.
    return {
        render : render
    };
}());


// --------------------------------------------------------
// cim.viewer.rendererForSimulation :: CIM view renderer that render cim simulation.
// N.B. Declared in a functional closure so as not to pollute global namespace.
// --------------------------------------------------------
cim.viewer.renderer.forSimulation = (function() {
    // Associated metadata used to generate view html.
    var myMetadata = cim.viewer.metadata.forSimulation;

    // Associated view options.
    var myOptions = cim.viewer.options.forSimulation;

    // Renders CIM model instance based upon passed options.
    // @cim         JSON encoded CIM instance (simulation).
    // @options     Rendering options.
    var render = function(cim, options) {
        // TODO
        alert('TODO - render simulations');
    };

    // Return rendering function.
    return {
        render : render
    };
}());
