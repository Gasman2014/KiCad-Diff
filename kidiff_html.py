# ------------------------------------------HTML Template Blocks-------------------------------------------
#
# FIXME These should go into external files to clean up and seperate the code


tail = '''
<div class="clearfix"></div>
<div style="padding:6px;"></div>
'''

indexHead = '''
<!DOCTYPE HTML>
<html lang="en">
<meta charset="utf-8" />
<head>
    <link rel="stylesheet" type="text/css" href="style.css" media="screen" />
</head>
<div class="responsivefull">
    <table style="border-color: #aaaaaa; width: 100%; height: 2px;" border="2px" cellspacing="2px" cellpadding="3px">
        <tbody>
            <tr>
                <td colspan="3" rowspan="3" width="45%">
                    <div class="title"> Title: {TITLE} </div>
                    <div class="details"> Company: {COMPANY} </div>
                </td>
                <td width="25%">
                    <div class="versions">Thickness (mm)</div>
                </td>
                <td width="15%">
                    <div class="versions green">{THICK1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{THICK2}</div>
                </td>
            </tr>
            <td width="25%">
                <div class="versions">Modules</div>
            </td>
            <td width="15%">
                <div class="versions green">{MODULES1}</div>
            </td>
            <td width="15%">
                <div class="versions red">{MODULES2}</div>
            </td>
            <tr>
                <td width="25%">
                    <div class="versions">Drawings</div>
                </td>
                <td width="15%">
                    <div class="versions green">{DRAWINGS1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{DRAWINGS2}</div>
                </td>
            </tr>
            <tr>
                <td width="15%">
                    <div class="versions">Version</div>
                </td>
                <td width="15%">
                    <div class="versions green">{diffDir1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{diffDir2}</div>
                </td>
                <td width="25%">
                    <div class="versions">Nets</div>
                </td>
                <td width="15%">
                    <div class="versions green">{NETS1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{NETS2}</div>
                </td>
            </tr>
            <tr>
                <td width="15%">
                    <div class="versions">Date</div>
                </td>
                <td width="15%">
                    <div class="versions">{D1DATE}</div>
                </td>
                <td width="15%">
                    <div class="versions">{D2DATE}</div>
                </td>
                <td width="25%">
                    <div class="versions">Tracks</div>
                </td>
                <td width="15%">
                    <div class="versions green">{TRACKS1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{TRACKS2}</div>
                </td>
            </tr>
            <tr>
                <td width="15%">
                    <div class="versions">Time</div>
                </td>
                <td width="15%">
                    <div class="versions">{D1TIME}</div>
                </td>
                <td width="15%">
                    <div class="versions">{D2TIME}</div>
                </td>
                <td width="25%">
                    <div class="versions">Zones</div>
                </td>
                <td width="15%">
                    <div class="versions green">{ZONES1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{ZONES2}</div>
                </td>
            </tr>
        </tbody>
    </table>
</div>
'''

outfile = '''
<div class="responsive">
  <div class="gallery">
    <a target="_blank" href="../{diff1}/{layername}">
    <a href="./tryptych/{prj}-{layer}.html"> <img class="{layer}" src="../{diff1}/{layername}" height="200"> </a>
    </a>
    <div class="desc">{layer}</div>
  </div>
</div>
'''

tryptychHTML = '''
<!DOCTYPE HTML>
<html lang="en">
<meta charset="utf-8" />
<head>
<link rel="stylesheet" type="text/css" href="../style.css" media="screen" />
<style>
div.responsive {{
   padding: 0 6px;
   float: left;
   width: 49.99%;
   }}
</style>
    <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.0/dist/svg-pan-zoom.min.js"></script>
</head>
<body>
<div class="title">{prj}</div>
<div class="subtitle">{layer}</div>


     <div id="compo-container" style="width: 100%; height: 800px;">
        <svg id="svg-id" xmlns="http://www.w3.org/2000/svg" style="display: inline; width: inherit; min-width: inherit; max-width: inherit; height: inherit; min-height: inherit; max-height: inherit;" version="1.1">
            <g>
                <svg id="compo">
                    <defs>
                        <filter id="f1">
                            <feColorMatrix id="c1" type="matrix" values="1   0   0   0   0
                  0   1   0   1   0
                  0   0   1   1   0
                  0   0   0   1   0 " />
                        </filter>
                    </defs>
                    <image x="0" y="0" height="100%" width="100%" filter="url(#f1)" xlink:href="../../{diff1}/{layername}" />
                </svg>

                <svg id="compo2">
                    <defs>
                        <filter id="f2">
                            <feColorMatrix id="c2" type="matrix" values="1   0   0   1   0
                  0   1   0   0   0
                  0   0   1   0   0
                  0   0   0   .5   0" />
                        </filter>
                    </defs>
                    <image x="0" y="0" height="100%" width="100%" filter="url(#f2)" xlink:href="../../{diff2}/{layername}" />
                </svg>
            </g>
        </svg>
    </div>

<div id="sbs-container"  width=100%; height=100% >
<embed id="diff1" class="{layer}" type="image/svg+xml" style="width: 50%; float: left; border:1px solid black;" src="../../{diff1}/{layername}" />
<embed id="diff2" class="{layer}" type="image/svg+xml" style="width: 50%; border:1px solid black;" src="../../{diff2}/{layername}" />
</div>

'''

twoPane = '''
<script>
        // Don't use window.onLoad like this in production, because it can only listen to one function.
        window.onload = function() {
            // Expose variable for testing purposes
            window.panZoomDiff = svgPanZoom('#svg-id', {
                zoomEnabled: true,
                controlIconsEnabled: true,
                center: true,
                minZoom: 1.5,
                maxZoom: 20,
            });
            // Expose variable to use for testing
            window.zoomDiff = svgPanZoom('#diff1', {
                zoomEnabled: true,
                controlIconsEnabled: true,
                minZoom: 1.5,
                maxZoom: 20,
                // Uncomment this in order to get Y asis synchronized pan
                // beforePan: function(oldP, newP) {return {y:false}},
            });

            // Expose variable to use for testing
            window.zoomDiff2 = svgPanZoom('#diff2', {
                zoomEnabled: true,
                controlIconsEnabled: true,
                minZoom: 1.5,
                maxZoom: 20,
            });

            zoomDiff.setOnZoom(function(level) {
                zoomDiff2.zoom(level)
                zoomDiff2.pan(zoomDiff.getPan())
            })

            zoomDiff.setOnPan(function(point) {
                zoomDiff2.pan(point)
            })

            zoomDiff2.setOnZoom(function(level) {
                zoomDiff.zoom(level)
                zoomDiff.pan(zoomDiff2.getPan())
            })

            zoomDiff2.setOnPan(function(point) {
                zoomDiff.pan(point)
            })

        };
</script>

</body>

</html>
'''

css = '''
body {
    background-color: #2c3031;
    margin: 0 auto;
    max-width: 45cm;
    border: 1pt solid #586e75;
    padding: 0.5em;
}

table {
    border-collapse: collapse;
    border-spacing: 0;
    border-color: #e2e3e3;
    width: 100%;
    height: 2px;
    border: 2px
}

html {
    background-color: #222222;
    color: #e2e3e3;
    margin: 1em;
}

.tabbed {
    float: left;
    width: 100%;
    padding: 0 6px;
}

.tabbed>input {
    display: none;
}

.tabbed>section>h1 {
    font: 14px arial, sans-serif;
    float: left;
    box-sizing: border-box;
    margin: 0;
    padding: 0.5em 0.1em 0;
    overflow: hidden;
    font-size: 1em;
    font-weight: normal;
}

.tabbed>input:first-child+section>h1 {
    padding-left: 1em;
}

.tabbed>section>h1>label {
    font: 14px arial, sans-serif;
    display: block;
    padding: 0.25em 0.75em;
    border: 1px solid #ddd;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    box-shadow: 0 0 0.5em rgba(0, 0, 0, 0.0625);
    background: rgb(50, 50, 50);
    cursor: pointer;
}

.tabbed>section>div {
    position: relative;
    z-index: 1;
    float: right;
    box-sizing: border-box;
    width: 100%;
    margin: 1.95em 0 0 -100%;
    padding: 0.25em 0.75em;
    border: 1px solid #ddd;

    box-shadow: 0 0 1em rgb(245, 245, 245);
    background: rgba(70, 67, 67, 0.185);
}

.tabbed>input:checked+section>h1 {
    position: relative;
    z-index: 2;
    border-bottom: none;
}


.tabbed>input:not(:checked)+section>div {
    display: none;
}

a:active,
a:hover {
    outline: 0;
}


.gallery {
    border: 1px solid #ccc;
    background-color: #222;
    padding: 5px;
    align: middle;
    vertical-align: middle;
}

.gallery:hover {
    border: 1px solid #777;
}

.gallery img {
    width: 100%;
    height: auto;
}

.desc,
.title {
    padding: 10px;
    text-align: center;
    font: 12px arial, sans-serif;
}

.title,
.subtitle,
.details {
    padding-left: 10px;
    text-align: left;
    font: 20px arial, sans-serif;
    color: #dddddd;
}

.subtitle {
    font: 14px arial, sans-serif;
}

.details,
.versions {
    padding: 5px;
    font: 12px arial, sans-serif;
    padding-bottom: 5px;
}


.differences {
    font: 12px courier, monospace;
    padding: 5px;
}

* {
    box-sizing: border-box;
}

.responsive {
    padding: 0 6px;
    float: left;
    width: 19.99999%;
    margin: 6px 0;
}

@media only screen and (max-width:700px) {
    .responsive {
        width: 49.98%;
        margin: 6px 0;
    }
}

@media only screen and (max-width:500px) {
    .responsive {
        width: 100%;
        margin: 6px 0;
    }
}

.responsivefull {
    padding: 0 6px;
    width: 100%;
    margin: 3px 0;
}

.clearfix:after {
    content: "";
    display: table;
    clear: both;
}

.box {
    float: left;
    width: 20px;
    height: 20px;
    margin: 5px;
    border: 1px solid rgba(0, 0, 0, .2);
}

.red {
    background: #832320;
}

.green {
    background: #44808aa8;
}


.added {
    color: #5eb6c4;
    text-align: left;
}

.removed {
    color: #ba312d;
    text-align: right;
}

.tbr td {
    color:#ba312d;
    padding: 10px;
    font: 12px arial,sans-serif;
    padding-bottom: 5px;
}

.tbl td {
    color: #5eb6c4;
    padding: 10px;
    font: 12px arial, sans-serif;
    padding-bottom: 5px;
}

.tbr th {
    text-align: left;
    background: #832320;
    padding: 10px;
    font: 12px arial, sans-serif;
    font-weight: bold;
    padding-bottom: 5px;
}

.tbl th {
    text-align: left;
    background: #44808aa8;
    padding: 10px;
    font: 12px arial, sans-serif;
    font-weight: bold;
    padding-bottom: 5px;
}

.F_Cu {
    filter: invert(28%) sepia(50%) saturate(2065%) hue-rotate(334deg) brightness(73%) contrast(97%);
}

.B_Cu {
    filter: invert(44%) sepia(14%) saturate(2359%) hue-rotate(70deg) brightness(103%) contrast(82%);
}

.B_Paste {
    filter: invert(91%) sepia(47%) saturate(4033%) hue-rotate(139deg) brightness(82%) contrast(91%);
}

.F_Paste {
    filter: invert(57%) sepia(60%) saturate(6%) hue-rotate(314deg) brightness(92%) contrast(99%);
}

.F_SilkS {
    filter: invert(46%) sepia(44%) saturate(587%) hue-rotate(132deg) brightness(101%) contrast(85%);
}

.B_SilkS {
    filter: invert(14%) sepia(27%) saturate(2741%) hue-rotate(264deg) brightness(95%) contrast(102%);
}

.B_Mask {
    filter: invert(22%) sepia(56%) saturate(2652%) hue-rotate(277deg) brightness(94%) contrast(87%);
}

.F_Mask {
    filter: invert(27%) sepia(51%) saturate(1920%) hue-rotate(269deg) brightness(89%) contrast(96%);
}

.Edge_Cuts {
    filter: invert(79%) sepia(79%) saturate(401%) hue-rotate(6deg) brightness(88%) contrast(88%);
}

.Margin {
    filter: invert(74%) sepia(71%) saturate(5700%) hue-rotate(268deg) brightness(89%) contrast(84%);
}

.In1_Cu {
    filter: invert(69%) sepia(39%) saturate(1246%) hue-rotate(17deg) brightness(97%) contrast(104%);
}

.In2_Cu {
    filter: invert(14%) sepia(79%) saturate(5231%) hue-rotate(293deg) brightness(91%) contrast(119%);
}

.Dwgs_User {
    filter: invert(40%) sepia(68%) saturate(7431%) hue-rotate(203deg) brightness(89%) contrast(98%);
}

.Cmts_User {
    filter: invert(73%) sepia(10%) saturate(1901%) hue-rotate(171deg) brightness(95%) contrast(102%);
}

.Eco1_User {
    filter: invert(25%) sepia(98%) saturate(2882%) hue-rotate(109deg) brightness(90%) contrast(104%);
}

.Eco2_User {
    filter: invert(85%) sepia(21%) saturate(5099%) hue-rotate(12deg) brightness(91%) contrast(102%);
}

.B_Fab {
    filter: invert(60%) sepia(0%) saturate(0%) hue-rotate(253deg) brightness(87%) contrast(90%);
}

.F_Fab {
    filter: invert(71%) sepia(21%) saturate(4662%) hue-rotate(21deg) brightness(103%) contrast(100%);
}

.B_Adhes {
    filter: invert(24%) sepia(48%) saturate(2586%) hue-rotate(218deg) brightness(88%) contrast(92%);
}

.F_Adhes {
    filter: invert(38%) sepia(49%) saturate(1009%) hue-rotate(254deg) brightness(88%) contrast(86%);
}

.B_CrtYd {
    filter: invert(79%) sepia(92%) saturate(322%) hue-rotate(3deg) brightness(89%) contrast(92%);
}

.F_CrtYd {
    filter: invert(73%) sepia(1%) saturate(0%) hue-rotate(116deg) brightness(92%) contrast(91%);
}
'''
