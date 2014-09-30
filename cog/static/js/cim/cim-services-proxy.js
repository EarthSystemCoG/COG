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
// cim.repository :: CIM repository (will be replaced by call to web-service).
// N.B. Declared in a functional closure so as not to pollute global namespace.
// N.B. Executes remote CIM web services.
// --------------------------------------------------------
window.cim.repository = {
    // Collection of models.
    'models' : [
        // HadGEM2-ES model.
        {
            cimInfo : {
                id : '309f6a26-e2b3-11df-bf17-00163e9152a5',
                version : '1',
                schema : '1.5',
                createDate : '2011-07-19T16:34:10.197064',
                source : 'Metafor CMIP5 Questionnaire',
                type : 'Model'
            },
            shortName : 'HadGEM2-ES',
            synonyms : 'HadGEM2',
            longName : 'Hadley Global Environment Model 2 - Earth System',
            description : 'The HadGEM2-ES model was a two stage development from HadGEM1, representing improvements in the physical model (leading to HadGEM2-AO) and the addition of earth system components and coupling (leading to HadGEM2-ES). [1] The HadGEM2-AO project targeted two key features of performance: ENSO and northern continent land-surface temperature biases. The latter had a particularly high priority in order for the model to be able to adequately model continental vegetation. Through focussed working groups a number of mechanisms that improved the performance were identified. Some known systematic errors in HadGEM1, such as the Indian monsoon, were not targeted for attention in HadGEM2-AO. HadGEM2-AO substantially improved mean SSTs and wind stress and improved tropical SST variability compared to HadGEM1. The northern continental warm bias in HadGEM1 has been significantly reduced. The power spectrum of El Nino is made worse, but other aspects of ENSO are improved. Overall there is a noticeable improvement from HadGEM1 to HadGEM2-AO when comparing global climate indices. [2] In HadGEM2-ES the vegetation cover is better than in the previous HadCM3LC model especially for trees, and the productivity is better than in the non-interactive HadGEM2-AO model. The presence of too much bare soil in Australia though may cause problems for the dust emissions scheme. The simulation of global soil and biomass carbon stores are good and agree well with observed estimates except in regions of errors in the vegetation cover. HadGEM2-ES compares well with the C4MIP ensemble of models. The distribution of NPP is much improved relative to HadCM3LC. At a site level the component carbon fluxes validate better against observations and in particular the timing of the growth season is significantly improved. The ocean biology (HadOCC) allows the completion of the carbon cycle and the provision of di-methyl sulphide (DMS) emissions from phytoplankton. DMS is a significant source of sulphate aerosol over the oceans. The diat-HadOCC scheme is an improvement over the standard HadOCC scheme as it differentiates between diatom and non-diatom plankton. These have different processes for removing carbon from the surface to the deep ocean, and respond differently to iron nutrients. The HadOCC scheme performs well with very reasonable plankton distributions, rates of productivity and emissions of DMS. The diat-HadOCC scheme has slightly too low levels of productivity which requires further tuning to overcome. The additions of a tropospheric chemistry scheme, new aerosol species (organic carbon and dust) and coupling between the chemistry and sulphate aerosols have significantly enhanced the earth system capabilities of the model. This has improved the tropospheric ozone distribution and the distributions of aerosol species compared to observations, both of which are important for climate forcing. Including interactive earth system components has not significantly affected the physical performance of the model.',
            parties : [
                { role : 'PI',
                  name : 'Chris Jones',
                  address : 'Met Office Hadley Centre, Fitzroy Road, Exeter, Devon, UK, EX1 3PB',
                  email : '--'
                },
                { role : 'funder',
                  name : 'UK Met Office Hadley Centre',
                  address : 'Met Office Hadley Centre, Fitzroy Road, Exeter, Devon, UK, EX1 3PB',
                  email : '--'
                },
                { role : 'contact',
                  name : 'Chris Jones',
                  address : 'Met Office Hadley Centre, Fitzroy Road, Exeter, Devon, UK, EX1 3PB',
                  email : '--'
                },
                { role : 'centre',
                  name : 'UK Met Office Hadley Centre',
                  address : 'Met Office Hadley Centre, Fitzroy Road, Exeter, Devon, UK, EX1 3PB',
                  email : '--'
                }
            ],
            citations : [
                { title : 'Bellouin et al. 2007',
                  type : 'Online Other',
                  reference : 'Bellouin N., O. Boucher, J. Haywood, C. Johnson, A. Jones, J. Rae, and S. Woodward. (2007) Improved representation of aerosols for HadGEM2.. Meteorological Office Hadley Centre, Technical Note 73, March 2007.',
                  location : 'http://www.metoffice.gov.uk/publications/HCTN/HCTN_73.pdf' },
                { title : 'Collins et al. 2008',
                  type : 'Online Other',
                  reference : 'Collins W.J. , N. Bellouin, M. Doutriaux-Boucher, N. Gedney, T. Hinton, C.D. Jones, S. Liddicoat, G. Martin, F. OConnor, J. Rae, C. Senior, I. Totterdell, and S. Woodward (2008) Evaluation of the HadGEM2 model. Meteorological Office Hadley Centre, Technical Note 74.',
                  location : 'http://www.metoffice.gov.uk/publications/HCTN/HCTN_74.pdf' }
            ],
            components : [
                { shortName : 'Aerosols',
                  longName : 'Aerosols',
                  description : 'The model includes interactive schemes for sulphate, sea salt, black carbon from fossil-fuel emissions, organic carbon from fossil-fuel emissions, mineral dust, and biomass-burning aerosols. The model also includes a fixed monthly climatology of mass-mixing ratios of secondary organic aerosols from terpene emissions (biogenic aerosols).',
                  type : 'Aerosols',
                  keyProperties : [
                      { name : 'biomass_burning',
                        units : 'kg/m2/s',
                        description : 'Emissions of aerosols from biomass burning injected at the surface for grassfires and homogeneously throughout the boundary layer for forest fire emissions. Represented as a monthly mean field on the N96 grid' },
                      { name : 'fossil_fuel_black_carbon',
                        units : 'kg/m2/s',
                        description : 'Emissions of primary black carbon from fossil fuel and biofuel injected at 80m as a monthly mean field on the N96 grid' },
                      { name : 'fossil_fuel_organic_carb',
                        units : 'kg/m2/s',
                        description : 'Emissions of primary organic carbon from fossil fuel and biofuel injected at 80m as a monthly mean field on the N96 grid' }
                  ]},
                { shortName : 'Atmosphere',
                  longName : 'Atmosphere',
                  description : 'The HadGEM2-ES model incorporates the Met Offices New Dynamics framework that provides a non-hydrostatic, fully compressible, deep atmosphere formulation with fewer approximations to the basic equations; semi-Lagrangian advection of all prognostic variables except density, permitting relatively long timesteps to be used at higher resolution; a conservative and monotone treatment of tracer transport; and improved geostrophic adjustment properties bringing better balance to the coupling. HadGEM2-ES includes interactive modelling of atmospheric aerosols, driven by surface and elevated emissions and including tropospheric chemical processes as well as physical removal processes such as washout. The aerosol species represented in the model are sulphate, black carbon, biomass smoke, sea salt, organic carbon, mineral dust and a biogenic climatology. The atmospheric component has a horizontal resolution of 1.25 degrees of latitude by 1.875 degrees of longitude with 38 layers in the vertical extending to over 39 km in height. The model uses the Arakawa C-grid horizontally and the Charney-Phillips grid vertically. The atmospheric timestep period is 30 minutes (48 timesteps per day).',
                  type : 'Atmosphere',
                  keyProperties : [
                      { name : 'anthro_SO2_aerosol',
                        units : 'kg/m2/s',
                        description : 'Anthropogenic sulphur dioxide emissions injected at the surface, except for energy emissions and half of industrial emissions which are injected at 0.5 km to represent chimney-level emissions.' },
                      { name : 'biogenic_emission_aeroso',
                        units : 'kg/kg',
                        description : '3D concentrations of organic aerosols from biogenic emissions. [CHECK cf name and short name]' },
                      { name : 'land DMS emissions',
                        units : 'kg/m2/s',
                        description : 'Constant for land-based emissions amounting to 0.86 Tg/yr from Spiro et al., 1992)' }
                  ]},
                { shortName : 'Atmospheric Chemistry',
                  longName : 'Atmospheric Chemistry',
                  description : 'The atmospheric chemistry component of HadGEM2-ES is a configuration of the United Kingdom Chemistry and Aerosols (UKCA) model (OConnor et al., 2009; 2010; www.ukca.ac.uk) running a relatively thorough description of inorganic odd oxygen (Ox), nitrogen (NOy), hydrogen (HOx), and carbon monoxide (CO) chemistry with near-explicit treatment of methane (CH4), ethane (C2H6), propane (C3H8), and acetone (Me2CO) degradation (including formaldehyde (HCHO), acetaldehyde (MeCHO), peroxy acetyl nitrate (PAN), and peroxy propionyl nitrate (PPAN)). It makes use of 25 tracers and represents 41 species. Large-scale transport, convective transport, and boundary layer mixing are treated. The chemistry scheme accounts for 25 photolytic reactions, 83 bimolecular reactions, and 13 uni- and termolecular reactions.',
                  type : 'Atmospheric Chemistry',
                  keyProperties : [
                      { name : 'acetaldehyde_emissions',
                        units : 'kg/m2/s',
                        description : 'Surface emissions of acetaldehyde, prescribed as annual quantities on the model grid' },
                      { name : 'acetone_emissions',
                        units : 'kg/m2/s',
                        description : 'Surface emissions of acetone, prescribed as annual quantities on the model grid' },
                      { name : 'aircraft_NOx_emissions',
                        units : 'kg/m2/s',
                        description : '3D emissions of nitrogen oxides from aircraft, prescribed as monthly quantities on the 3D model grid.' }
                  ]},
                { shortName : 'Land Ice',
                  longName : 'Land Ice',
                  description : 'The major ice sheets (Greenland and Antarctica), and minor ice caps (Ellesmere, Devon and Baffin islands, Iceland, Svalbard, Novaya and Severnaya Zemlya, and Stikine) are depicted as static ice. They are initialised with a snow depth of 50,000 mm of water equivalent. Further ablation or accumulation has an impact on sea level. Runoff follows the river routing scheme and enters the oceans at predefined river outflow points. Calving at the coastal boundaries is simulated through a fresh water flux to the ocean evenly distributed over the area of observed icebergs in both hemispheres. The value of the freshwater flux is calculated to exactly balance the time mean ice sheet surface mass balance over the preindustrial control simulation.',
                  type : 'Land Ice',
                  keyProperties : [
                      { name : 'LandIceAlbedo',
                        units : '',
                        description : 'prescribed' }
                  ]},
                { shortName : 'Land Surface',
                  longName : 'Land Surface',
                  description : 'The second version of the U.K. Met Office Surface Exchange Scheme (MOSES-II) (Cox et al. 1999; Essery et al. 2003) is used. This allows tiling of land surface heterogeneity using nine different surface types. A separate surface energy balance is calculated for each tile and area-weighted grid box mean fluxes are computed, which are thus much more realistic than when a single surface type is assumed. In addition, vegetation leaf area is allowed to vary seasonally, providing a more realistic representation of seasonal changes in surface fluxes. Tiling of coastal grid points allows separate treatment of land and sea fractions. This in combination with the increased ocean model resolution greatly improves the coastline, particularly in island regions.',
                  type : 'Land Surface',
                  keyProperties : [
                      { name : 'changing_anthro_land_use',
                        units : 'dimensionless value between 0 and 1',
                        description : 'Time varying fractional mask of anthropogenic disturbance' },
                      { name : 'initial_land_use',
                        units : 'dimensionless value between 0 and 1',
                        description : 'Prescribed fractions of urban areas, lakes, ice, broadleaf tree, needleleaf tree, C3 grass, C4 grass, shrub and bare soil' },
                      { name : 'well_mixed_gas_CO2',
                        units : 'kg/kg',
                        description : 'CO2 concentrations prescribed as a single global constant provided as an annual number but interpolated in the model at each timestep. Provided as a mass mixing ratio with units of kg/kg. CO2 concentrations are passed to the models radiation scheme, terrestrial carbon cycle and ocean carbon cycle.' }
                  ]},
                { shortName : 'Ocean',
                  longName : 'Ocean',
                  description : 'The ocean component is based on the Bryan-Cox code (Bryan 1969; Cox 1984) and follows the ocean component of HadGEM1 (Johns et al., 2006) very closely. The model uses a latitude-longitude grid with a zonal resolution of 1 degree, and a meridional resolution of 1 degree between the poles and 30 degrees, from which it increases smoothly to 0.333 degrees at the equator - giving a grid of 360 x 216 points. It has 40 unevenly spaced levels in the vertical, with enhanced resolution near the surface better to resolve the mixed layer and thermocline. The forward timestep period is 1 hour, with a mixing timestep of once per day. HadGEM2 uses a bathymetry derived from the Smith and Sandwell (1997) 1/30 degrees depth dataset merged with ETOPO5 (1988) 1/12 degrees data at high latitudes, interpolated to the model grid and smoothed using a five-point (1:4:1) two-dimensional filter. Where this procedure obstructs important narrow pathways (e.g., Denmark Strait, Faroes-Shetland Channel, Vema Channel, and around the Indonesian archipelago), the bathymetry is adjusted to allow some flow at realistic depths (with reference to Thompson 1995). The land masks for the ocean grid differs from that used for the atmosphere model, due to the differences in model resolutions. To enable daily coupling between the models a tiling scheme has been introduced. For each atmosphere grid box, fractions of the fluxes can be coupled to land, sea and sea ice models so that the total flux is conserved - though locally the flux may not be conserved so diagnosis can be difficult. The only ancillary flux used by the ocean model is to enable a balance in the freshwater flux to be maintained, since the accumulation of frozen water on land is not returned into the freshwater cycle, i.e there is no representation of icebergs calving off ice shelves. The ancillary flux is used to add freshwater back into the model, calibrated from a HadGEM2 reference integration to give a balanced freshwater budget.',
                  type : 'Ocean',
                  keyProperties : [
                      { name : 'Ocean Key Properties',
                        units : '',
                        description : 'The sea water formulation of the equation of state is following that of UNESCO.' },
                      { name : 'well_mixed_gas_CO2',
                        units : 'kg/kg',
                        description : 'CO2 concentrations prescribed as a single global constant provided as an annual number but interpolated in the model at each timestep. Provided as a mass mixing ratio with units of kg/kg. CO2 concentrations are passed to the models ocean carbon cycle.' }
                  ]},
                { shortName : 'Ocean Biogeo Chemistry',
                  longName : 'Ocean Biogeo Chemistry',
                  description : 'There is a simple prognostic ecosystem model (the Diat-HadOCC model), with three nutrients (combined nitrate and ammonium, dissolved silicate and dissolved iron), two phytoplankton (diatoms and other phytoplankton), one zooplankton and three detrital compartments (detrital nitrogen, detrital carbon and detrital silicate). There are also two prognostic tracers that are only used in a diagnostic capacity (i.e. their concentrations are affected by, but do not affect, the other compartments): these are dissolved ammonium and dissolved oxygen. Nitrogen is used as the model currency. The diatoms have a variable silicate:nitrate ratio, so diatom silicate is another compartment. All three of the detrital compartments sink with a constant velocity, and are remineralised at a rate that is depth-dependent The zooplankton and both phytoplankton compartments have fixed elemental carbon:nitrogen ratios which allow the flows of carbon through the ecosystem to be linked to the corresponding nitrogen flows. As well as the ecosystem compartments listed above dissolved inorganic carbon (DIC) and total alkalinity (TAlk) are included as prognostic tracers. Those two compartments, along with the model temperature and salinity, are used to calculate the ocean surface pCO2, the air-sea flux of CO2 and the ocean pH. The air-sea fluxes of CO2 and DMS are each calculated every ocean time-step and their daily means are passed through the coupler to the atmosphere each day.',
                  type : 'Ocean Biogeo Chemistry',
                  keyProperties : [
                      { name : 'BasicApproximations',
                        units : '',
                        description : 'Eulerian model, N3 P2 Z1 D1 ecosystem; no diel cycle, constant detrital sinking rate, constant (carbonate) rain ratio.' },
                      { name : 'ListOfPrognosticVariables',
                        units : '',
                        description : 'Dissolved inorganic nitrogen (nitrate+ammonia); dissolved silicate; dissolved iron; diatoms; other phytoplankton; zooplankton; diatom silicate; detrital nitrogen; detrital carbon; detrital silicate; dissolved inorganic carbon; total alkalinity; dissolved oxygen.' }
                  ]},
            ]
        },

        // MPI-ESM-LR model.
        {
            cimInfo : {
                id : '8a6778c6-daa9-11df-b8ba-00163e9152a5',
                version : '3',
                schema : '1.5',
                createDate : '2011-09-22T13:21:14.832846',
                source : 'Metafor CMIP5 Questionnaire',
                type : 'Model'
            },
            shortName : 'MPI-ESM-LR',
            synonyms : 'MPEH5',
            longName : 'MPI Earth System Model running on low resolution grid',
            description : 'ECHAM6 and JSBACH / MPIOM and HAMOCC coupled via OASIS3.',
            parties : [
                { role : 'PI',
                  name : 'Marco Giorgetta',
                  address : 'Department (modelling group): Atmosphäre im Erdsystem',
                  email : 'marco.giorgetta@zmaw.de'
                },
                { role : 'funder',
                  name : 'Max Planck Institute for Meteorology',
                  address : '--',
                  email : '--'
                },
                { role : 'contact',
                  name : 'cmip5-mpi-esm',
                  address : '--',
                  email : '--'
                },
                { role : 'centre',
                  name : 'Max Planck Institute for Meteorology',
                  address : '--',
                  email : '--'
                }
            ],
            citations : [
                { title : 'HAMMOC',
                  type : 'Online Other',
                  reference : 'HAMOCC: Technical Documentation',
                  location : 'http://www.mpimet.mpg.de/fileadmin/models/MPIOM/HAMOCC5.1_TECHNICAL_REPORT.pdf' },
                { title : 'Marsland_etal_2003',
                  type : 'Online Refereed',
                  reference : 'Marsland, S. J., H. Haak, J. H. Jungclaus, M. Latif and F. Roeske, 2003: The Max-Planck-Institute global ocean/sea ice model with orthogonal curvilinear coordinates.", Ocean Modelling, 5, 91-127.',
                  location : '--' },
                { title : 'Raddatz_etal_2007',
                  type : 'Online Refereed',
                  reference : '"Raddatz T.J., Reick C.H., Knorr W., Kattge J., Roeckner E., Schnur R., Schnitzler K.-G., Wetzel P., Jungclaus J., 2007:Will the tropical land biosphere dominate the climate-carbon cycle feedback during the twenty first century?",Climate Dynamics, 29, 565-574, doi 10.1007/s00382-007-0247-8.',
                  location : '--' }

            ],
            components : [
                { shortName : 'ECHAM6',
                  longName : 'ECHAM6 atmospheric global general circulation model',
                  description : 'The land vegetation module JSBACH is integrated module of the ECHAM6 code but can run stand alone.',
                  type : 'Aerosols',
                  keyProperties : [
                      { name : 'biomass_burning',
                        units : 'kg/m2/s',
                        description : 'Emissions of aerosols from biomass burning injected at the surface for grassfires and homogeneously throughout the boundary layer for forest fire emissions. Represented as a monthly mean field on the N96 grid' },
                      { name : 'fossil_fuel_black_carbon',
                        units : 'kg/m2/s',
                        description : 'Emissions of primary black carbon from fossil fuel and biofuel injected at 80m as a monthly mean field on the N96 grid' },
                      { name : 'fossil_fuel_organic_carb',
                        units : 'kg/m2/s',
                        description : 'Emissions of primary organic carbon from fossil fuel and biofuel injected at 80m as a monthly mean field on the N96 grid' }
                  ]},
                { shortName : 'HAMOCC',
                  longName : 'Hamburg Model of Ocean Carbon Cycle',
                  description : 'HAMOCC is a sub-model that simulates biogeochemical tracers in the oceanic water column and in the sediment. All biogeochemical tracers are fully advected and mixed by the hosting OGCM (MPIOM). The biogeochemical model itself is driven by the same radiation as the OGCM to compute photosynthesis. Temperature and salinity are used to calculate various transformation rates and constants e.g., for solubility of carbon dioxide.',
                  type : 'OceanBiogeoChemistry',
                  keyProperties : [
                      { name : 'anthro_SO2_aerosol',
                        units : 'kg/m2/s',
                        description : 'Anthropogenic sulphur dioxide emissions injected at the surface, except for energy emissions and half of industrial emissions which are injected at 0.5 km to represent chimney-level emissions.' },
                      { name : 'biogenic_emission_aeroso',
                        units : 'kg/kg',
                        description : '3D concentrations of organic aerosols from biogenic emissions. [CHECK cf name and short name]' },
                      { name : 'land DMS emissions',
                        units : 'kg/m2/s',
                        description : 'Constant for land-based emissions amounting to 0.86 Tg/yr from Spiro et al., 1992)' }
                  ]},
                { shortName : 'JSBACH',
                  longName : 'JSBACH',
                  description : 'JSBACH can be run as stand alone model, but is an integrated code part of ECHAM6.',
                  type : 'LandSurface',
                  keyProperties : [
                      { name : 'acetaldehyde_emissions',
                        units : 'kg/m2/s',
                        description : 'Surface emissions of acetaldehyde, prescribed as annual quantities on the model grid' },
                      { name : 'acetone_emissions',
                        units : 'kg/m2/s',
                        description : 'Surface emissions of acetone, prescribed as annual quantities on the model grid' },
                      { name : 'aircraft_NOx_emissions',
                        units : 'kg/m2/s',
                        description : '3D emissions of nitrogen oxides from aircraft, prescribed as monthly quantities on the 3D model grid.' }
                  ]},
                { shortName : 'MPIOM',
                  longName : 'Max - Planck Institute Ocean Model in low resolution',
                  description : 'The Max- Planck- Institute ocean model (MPIOM) is the ocean- sea ice component of the Max- Planck- Institute climate model (Roeckner et al., 2006; Jungclaus et al., 2006). It includes an embedded dynamic/ thermodynamic sea ice model with a viscous- plastic rheology following Hibler (1979) and a bottom boundary layer scheme for the flow across steep topography. A model descriptin can be found at Marsland et al. (2003). Furthermore the ocean biogeochemical modul HAMOCC is an integrated module of the MPI-OM code, but can run stand alone.',
                  type : 'Ocean',
                  keyProperties : [
                      { name : 'LandIceAlbedo',
                        units : '',
                        description : 'prescribed' }
                  ]},
                { shortName : 'Sea Ice',
                  longName : 'MPIOM SeaIceComponent',
                  description : 'Sea ice component is included in MPI-OM, It includes an embedded dynamic/ thermodynamic sea ice model with a viscous- plastic rheology following Hibler (1979).',
                  type : 'SeaIce',
                  keyProperties : [
                      { name : 'changing_anthro_land_use',
                        units : 'dimensionless value between 0 and 1',
                        description : 'Time varying fractional mask of anthropogenic disturbance' },
                      { name : 'initial_land_use',
                        units : 'dimensionless value between 0 and 1',
                        description : 'Prescribed fractions of urban areas, lakes, ice, broadleaf tree, needleleaf tree, C3 grass, C4 grass, shrub and bare soil' },
                      { name : 'well_mixed_gas_CO2',
                        units : 'kg/kg',
                        description : 'CO2 concentrations prescribed as a single global constant provided as an annual number but interpolated in the model at each timestep. Provided as a mass mixing ratio with units of kg/kg. CO2 concentrations are passed to the models radiation scheme, terrestrial carbon cycle and ocean carbon cycle.' }
                  ]}
            ]
        },
    ],

    dataObjects : [
        {
            acronym : 'HADGEM2_20C3M_1_D0_mrsos1',
            description : 'This dataset represents daily output: instantaneous daily values at 0UTC (D0) or daily averaged/accumulated/max/min values (DM) of the selected variable for ENSEMBLES. The model output was prepared for the IPCC Fourth Assessment 20C3M experiment. For specific scenario details see experiment summary. These data are in netCDF format.',
            dataContent : {
                name : 'moisture_content_of_soil_layer',
                description : 'moisture_content_of_soil_layer [CF-Standard Name]',
                standardName : 'moisture_content_of_soil_layer',
                units : 'm s-1',
                aggregation : 'sum',
                frequency : 'Other'
            }
        }
    ]
};



// --------------------------------------------------------
// cim.servicesProxy :: CIM services proxy.
// N.B. Declared in a functional closure so as not to pollute global namespace.
// N.B. Executes remote CIM web services.
// --------------------------------------------------------
window.cim.servicesProxy = (function() {

    // Instance of mocked cim repository.
    var _repository = window.cim.repository;
    
    // Module level error handler.
    // @exception   Exception that has occurred processing a request.
    // @onError     Callback to invoke when function unsucessfully executes.
    var _errorHandler = function(exception, operation, onError) {
        var error;      // Error message to be returned.

        // Invoke client error handler (if specified).
        if (_.isFunction(onError) === true) {
            onError(exception, operation);
        
        // Otherwise perform default tasks.
        } else {
            error = "CIM web service processing error:\n";
            error += "\tOperation\t: "+ operation + "\n";
            error += "\tError\t\t: " + exception.message + "\n";
            alert(error);
        }
    };

    // Object wrapped in functional closure to avaoid global namespace pollution.
    return {
        // Query service executes search against backend CIM repository.
        query : {
            // Gets a model.
            // @project         Project with which model is associated.
            // @name            Short Name of model being returned.
            // @onSuccess       Callback to invoke when function sucessfully executes.
            // @onError         Callback to invoke when function unsucessfully executes.
            getModelByName : function (project, name, onSuccess, onError) {
                var result;      // Model to be returned.

                // Search for model against CIM repository web-service.
                try {
                    // Search by short name.
                    result = _(_repository.models).detect(function(m) {
                        return m.shortName.toUpperCase() === name.toUpperCase();
                    });

                    // If not found search by synonym.
                    if (result === undefined) {
                        result = _(_repository.models).detect(function(m) {
                            return m.synonyms.toUpperCase().search(name.toUpperCase()) !== -1;
                        });
                    }

                    // If not found return first.
                    if (result === undefined) {
                        result = _.first(_repository.models);
                    }
                }
                catch(exception) {
                    _errorHandler(exception, 'query.getModelByName', onError);
                }                

                // Invoke callback (if specified).
                if (_.isFunction(onSuccess) === true) {
                    onSuccess(result);
                }

                return result;
            },

            // Gets a data object by acronym.
            // @project         Project with which data object is associated.
            // @acronym         Name of data object being returned.
            // @onSuccess       Callback to invoke when function sucessfully executes.
            // @onError         Callback to invoke when function unsucessfully executes.
            getDataObjectByAcronym : function (project, acronym, onSuccess, onError) {
                var result;      // data object to be returned.

                // Search for data object against CIM repository web-service.
                try {
                    // TODO
                }
                catch(exception) {
                    _errorHandler(exception, 'query.getDataObjectByAcronym', onError);
                }

                // Invoke callback (if specified).
                if (_.isFunction(onSuccess) === true) {
                    onSuccess(result);
                }

                return result;
            },

            // Gets a experiment by name.
            // @project         Project with which experiment is associated.
            // @name            Name of data object being returned.
            // @onSuccess       Callback to invoke when function sucessfully executes.
            // @onError         Callback to invoke when function unsucessfully executes.
            getExperimentByName : function (project, name, onSuccess, onError) {
                var result;      // Experiment to be returned.

                // Search for experiment against CIM repository web-service.
                try {
                    // TODO
                }
                catch(exception) {
                    _errorHandler(exception, 'query.getExperimentByName', onError);
                }

                // Invoke callback (if specified).
                if (_.isFunction(onSuccess) === true) {
                    onSuccess(result);
                }

                return result;
            },

            // Gets a simulation by name.
            // @project         Project with which simulation is associated.
            // @name            Name of data object being returned.
            // @onSuccess       Callback to invoke when function sucessfully executes.
            // @onError         Callback to invoke when function unsucessfully executes.
            getSimulationByName : function (project, name, onSuccess, onError) {
                var result;      // Simulation to be returned.

                // Search for simulation against CIM repository web-service.
                try {
                    // TODO
                }
                catch(exception) {
                    _errorHandler(exception, 'query.getSimulationByName', onError);
                }

                // Invoke callback (if specified).
                if (_.isFunction(onSuccess) === true) {
                    onSuccess(result);
                }

                return result;
            }
        }
    };
}());

