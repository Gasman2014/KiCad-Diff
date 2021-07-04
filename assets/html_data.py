# HTML Data
# Intermediate approach before something better

indexHead = """
<!DOCTYPE HTML>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <link rel="icon" href="http://127.0.0.1:9092/favicon.ico" type="image/x-icon" />
    <link rel="shortcut icon" href="favicon.ico" type="image/x-icon" />
    <link rel="stylesheet" type="text/css" href="style.css" media="screen" />
    <title>{board_title}</title>
</head>

<div class="responsivefull">
    <table style="border-color: #aaaaaa; width: 100%; height: 2px;" border="2px" cellspacing="2px" cellpadding="3px">
        <tbody>
            <tr>
                <td colspan="3" rowspan="3" width="45%">
                    <div class="title"> Board: {board_title} </div>
                    <div class="details"> Company: {board_company} </div>
                </td>
                <td width="25%">
                    <div class="versions">Thickness (mm)</div>
                </td>
                <td width="15%">
                    <div class="versions green">{thickness1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{thickness2}</div>
                </td>
            </tr>
            <td width="25%">
                <div class="versions">Modules</div>
            </td>
            <td width="15%">
                <div class="versions green">{modules1}</div>
            </td>
            <td width="15%">
                <div class="versions red">{modules2}</div>
            </td>
            <tr>
                <td width="25%">
                    <div class="versions">Drawings</div>
                </td>
                <td width="15%">
                    <div class="versions green">{drawings1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{drawings2}</div>
                </td>
            </tr>
            <tr>
                <td width="15%">
                    <div class="versions">Version</div>
                </td>
                <td width="15%">
                    <div class="versions green">{hash1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{hash2}</div>
                </td>
                <td width="25%">
                    <div class="versions">Nets</div>
                </td>
                <td width="15%">
                    <div class="versions green">{nets1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{nets2}</div>
                </td>
            </tr>
            <tr>
                <td width="15%">
                    <div class="versions">Date</div>
                </td>
                <td width="15%">
                    <div class="versions green">{date1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{date2}</div>
                </td>
                <td width="25%">
                    <div class="versions">Tracks</div>
                </td>
                <td width="15%">
                    <div class="versions green">{tracks1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{tracks2}</div>
                </td>
            </tr>
            <tr>
                <td width="15%">
                    <div class="versions">Time</div>
                </td>
                <td width="15%">
                    <div class="versions green">{time1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{time2}</div>
                </td>
                <td width="25%">
                    <div class="versions">Zones</div>
                </td>
                <td width="15%">
                    <div class="versions green">{zones1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{zones2}</div>
                </td>
            </tr>
        </tbody>
    </table>
</div>
"""

outfile = """
<div class="responsive">
    <div class="gallery">
        <a target="_blank" href="../{hash1}/{filename_svg}">
            <a href="./triptych/{triptych_html}">
                <img class="{layer_class}" src="../{hash1}/{filename_svg}" height="200">
            </a>
        </a>
        <div class="desc">{index} - {layer_name}</div>
    </div>
</div>
"""

triptychHTML = """
<!DOCTYPE HTML>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <link rel="icon" href="http://127.0.0.1:9092/favicon.ico" type="image/x-icon" />
    <link rel="shortcut icon" href="../favicon.ico" type="image/x-icon" />
    <link rel="stylesheet" type="text/css" href="../style.css" media="screen" />
    <style>
        div.responsive {{
            padding: 0 6px;
            float: left;
            width: 49.99%;
    }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>

    <script type="text/javascript">
        var keysDown = {{}};
        window.onkeydown = function(e) {{
            keysDown[e.key] = true;
            if (keysDown.ArrowLeft) {{
                keysDown = {{}};
                document.location.href = "/web/triptych/{previous_page}";
            }};
            if (keysDown.ArrowRight) {{
                keysDown = {{}};
                document.location.href = "/web/triptych/{next_page}";
            }};
            if (keysDown.h || keysDown.H || e.which === 32) {{
                keysDown = {{}};
                document.location.href = "/web/";
            }};
        }}
    </script>
</head>
<body>

    <div id="compo-container" style="width: 100%; height: 600px; position: relative;">
        <div style="position: absolute; width: 100%; height: inherit;">
            <svg id="svg-id" xmlns="http://www.w3.org/2000/svg" style="display: inline; width: inherit; min-width: inherit; max-width: inherit; height: inherit; min-height: inherit; max-height: inherit;" version="1.1">
                <g>
                    <svg id="compo">
                        <defs>
                            <filter id="f1">
                                <feColorMatrix id="c1" type="matrix"
                                    values="1   0   0   0   0
                                            0   1   0   1   0
                                            0   0   1   1   0
                                            0   0   0   1   0" />
                            </filter>
                        </defs>
                        <image x="0" y="0" height="100%" width="100%" filter="url(#f1)" xlink:href="../../{hash1}/{filename_svg}" />
                    </svg>
                    <svg id="compo2">
                        <defs>
                            <filter id="f2">
                                <feColorMatrix id="c2" type="matrix"
                                    values="1   0   0   1   0
                                            0   1   0   0   0
                                            0   0   1   0   0
                                            0   0   0  .5   0" />
                            </filter>
                        </defs>
                        <image x="0" y="0" height="100%" width="100%" filter="url(#f2)" xlink:href="../../{hash2}/{filename_svg}" />
                    </svg>
                </g>
            </svg>
        </div>
        <div style="background: rgba(255, 0, 0, 0.0); z-index: 10; position: absolute;" class="subtitle">{index}. {layer_name}</div>
    </div>

    <div id="sbs-container" style="position:relative; width: 100%; border:1px solid #555; background-color: #222; text-align: center; display: flex;">

        <div id="image1-container" style="border: 1px solid #555; width: 50%; height: 250px">
            <div style="width: 100%; height: 250px">
                <svg id="svg-img1-id" xmlns="http://www.w3.org/2000/svg"
                    style="display: inline; width: 100%; min-width: 100%; max-width: 100%; height: 100%; min-height: 100%; max-height: 100%;"
                    version="1.1" class="{layer_class}">
                    <svg id="image_1">
                        <image x="0" y="0" height="100%" width="100%" xlink:href="../../{hash1}/{filename_svg}"/>
                    </svg>
                </svg>
            </div>
        </div>

        <div id="image2-container" style="border: 1px solid #555; width: 50%; height: 250px">
            <div style="width: 100%; height: 250px">
                <svg id="svg-img2-id" xmlns="http://www.w3.org/2000/svg" style="display: inline; width: 100%; min-width: 100%; max-width: 100%;
                    height: 100%; min-height: 100%; max-height: 100%;"
                    version="1.1"  class="{layer_class}">
                    <svg id="image_2">
                       <image x="0" y="0" height="100%" width="100%" xlink:href="../../{hash2}/{filename_svg}"/>
                    </svg>
                </svg>
            </div>
        </div>

    </div>
"""

twopane = """
<script>
    window.onload = function() {

        var panZoomDiff = svgPanZoom(
            '#svg-id', {
                zoomEnabled: true,
                controlIconsEnabled: true,
                center: true,
                minZoom: 1.0,
                maxZoom: 20,
            }
        );

        var zoomDiff1 = svgPanZoom(
            '#image_1', {
                zoomEnabled: true,
                controlIconsEnabled: true,
                center: true,
                minZoom: 1.0,
                maxZoom: 20,
            }
        );

        var zoomDiff2 = svgPanZoom(
            '#image_2', {
                zoomEnabled: true,
                controlIconsEnabled: true,
                minZoom: 1.0,
                maxZoom: 20,
            }
        );

        zoomDiff1.setOnZoom(
            function(level) {
                zoomDiff2.zoom(level);
                zoomDiff2.pan(zoomDiff1.getPan());
            }
        );

        zoomDiff1.setOnPan(
            function(point) {
                zoomDiff2.pan(point);
            }
        );

        zoomDiff2.setOnZoom(
            function(level) {
                zoomDiff1.zoom(level);
                zoomDiff1.pan(zoomDiff2.getPan());
            }
        );

        zoomDiff2.setOnPan(
            function(point) {
                zoomDiff1.pan(point);
            }
        );


    };
</script>

</body>
</html>
"""

tail = """
<div class="clearfix"></div>
<div style="padding:6px;"></div>
"""
