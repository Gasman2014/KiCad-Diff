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
    <table style="border-color: #555555; width: 100%; height: 2px;" border="2px" cellspacing="2px" cellpadding="3px">
        <tbody>
            <tr>
                <td colspan="3" rowspan="3" width="45%">
                    <div class="title"> {board_title} </div>
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
    <script integrity="" src="https://code.jquery.com/jquery-3.5.0.js"></script>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
    <script integrity="" src="https://code.iconify.design/1/1.0.7/iconify.min.js"></script>
    <link rel="stylesheet" type="text/css" href="../style.css" media="screen" />
    <title>{board_title} - {layer_name}</title>
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
                document.location.href = "{previous_page}";
            }};
            if (keysDown.ArrowRight) {{
                keysDown = {{}};
                document.location.href = "{next_page}";
            }};
            if (keysDown.h || keysDown.H || e.which === 32) {{
                keysDown = {{}};
                document.location.href = "../../../{homebase}";
            }};
        }}
    </script>
</head>
<body>

    <div id="compo-container" style="width: 100%; height: 600px; position: relative;">

        <div style="position: absolute; width: 100%; height: inherit;">
            <svg id="svg-compo-diff" xmlns="http://www.w3.org/2000/svg" style="display: inline; width: inherit; min-width: inherit; max-width: inherit; height: inherit; min-height: inherit; max-height: inherit;" version="1.1">
                <g>
                    <svg id="compo1">
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

        <div style="background: rgba(255, 0, 0, 0.0); z-index: 10; position: absolute; margin-top: 10px">
            <span class="title">{board_title}</span><br>
            <span class="subtitle">{index}. {layer_name}</span>
        </div>

        <div class="diff-controls" style="background: rgba(255, 0, 0, 0.0); z-index: 10; position: absolute; top:10px; right: 0px; padding-right: 10px">
            <button class="btn btn-dark" id="diff-zoom-in">
                <span class="iconify" style="width: 20px; height: 20px;" data-icon="akar-icons:zoom-in" data-inline="false"></span>
            </button>
            <button class="btn btn-dark" id="diff-zoom-out">
                <span class="iconify" style="width: 20px; height: 20px;" data-icon="akar-icons:zoom-out" data-inline="false"></span>
            </button>
            <button class="btn btn-dark" id="diff-reset">
                <span class="iconify" style="width: 20px; height: 20px;" data-icon="carbon:center-to-fit" data-inline="false"></span>
            </button>
        </div>
    </div>

    <div id="sbs-container" style="position:relative; width: 100%; background-color: #222; text-align: center; display: flex;">

        <div id="image1-container" style="border: 1px solid #555; width: 50%; height: 250px">
            <div style="background: rgba(255, 0, 0, 0.0); z-index: 10; position: absolute; padding-left: 10px" class="subtitle">{hash1}</div>
            <div style="width: 100%; height: 250px">
                <svg id="svg-img1-id" xmlns="http://www.w3.org/2000/svg"
                    style="display: inline; width: 100%; min-width: 100%; max-width: 100%; height: 100%; min-height: 100%; max-height: 100%;"
                    version="1.1" class="{layer_class}">
                    <svg id="image_1">
                        <image x="0" y="0" height="100%" width="100%" xlink:href="../../{hash1}/{filename_svg}"/>
                    </svg>
                </svg>
                <div class="hash1-controls" style="background: rgba(255, 0, 0, 0.0); z-index: 10; position: absolute; top:10px; right: 50%; padding-right: 10px">
                    <button class="btn btn-dark" id="hash1-zoom-in">
                        <span class="iconify" style="width: 20px; height: 20px;" data-icon="akar-icons:zoom-in" data-inline="false"></span>
                    </button>
                    <button class="btn btn-dark" id="hash1-zoom-out">
                        <span class="iconify" style="width: 20px; height: 20px;" data-icon="akar-icons:zoom-out" data-inline="false"></span>
                    </button>
                    <button class="btn btn-dark" id="hash1-reset">
                        <span class="iconify" style="width: 20px; height: 20px;" data-icon="carbon:center-to-fit" data-inline="false"></span>
                    </button>
                </div>
            </div>
        </div>

        <div id="image2-container" style="border: 1px solid #555; width: 50%; height: 250px">
            <div style="background: rgba(255, 0, 0, 0.0); z-index: 10; position: absolute; padding-left: 10px" class="subtitle">{hash2}</div>
            <div style="width: 100%; height: 250px">
                <svg id="svg-img2-id" xmlns="http://www.w3.org/2000/svg" style="display: inline; width: 100%; min-width: 100%; max-width: 100%;
                    height: 100%; min-height: 100%; max-height: 100%;"
                    version="1.1"  class="{layer_class}">
                    <svg id="image_2">
                        <image x="0" y="0" height="100%" width="100%" xlink:href="../../{hash2}/{filename_svg}"/>
                    </svg>
                </svg>
            </div>
            <div class="hash2-controls" style="background: rgba(255, 0, 0, 0.0); z-index: 10; position: absolute; top:10px; right: 0px; padding-right: 10px">
                <button class="btn btn-dark" id="hash2-zoom-in">
                    <span class="iconify" style="width: 20px; height: 20px;" data-icon="akar-icons:zoom-in" data-inline="false"></span>
                </button>
                <button class="btn btn-dark" id="hash2-zoom-out">
                    <span class="iconify" style="width: 20px; height: 20px;" data-icon="akar-icons:zoom-out" data-inline="false"></span>
                </button>
                <button class="btn btn-dark" id="hash2-reset">
                    <span class="iconify" style="width: 20px; height: 20px;" data-icon="carbon:center-to-fit" data-inline="false"></span>
                </button>
            </div>
        </div>
    </div>
"""

twopane = """
<script>

    var pan_zoom_diff;
    var pan_zoom_hash1;
    var pan_zoom_hash2;

    window.onload = function() {

        pan_zoom_diff = svgPanZoom(
            '#svg-compo-diff', {
                zoomEnabled: true,
                center: true,
                minZoom: 1.0,
                maxZoom: 20,
                controlIconsEnabled: false,
                zoomScaleSensitivity: 0.1,
                fit: false
            }
        );

        document.getElementById('diff-zoom-in').addEventListener(
            'click', function(ev) {
                ev.preventDefault();
                pan_zoom_diff.zoomIn();
                console.log("diff-zoom-in");
            }
        );

        document.getElementById('diff-zoom-out').addEventListener(
            'click', function(ev) {
                ev.preventDefault();
                pan_zoom_diff.zoomOut();
                console.log("diff-zoom-out");
            }
        );

        document.getElementById('diff-reset').addEventListener(
            'click', function(ev) {
                ev.preventDefault();
                pan_zoom_diff.resetZoom();
                console.log("diff-zoom-reset");
            }
        );

        /***************************************************/

        pan_zoom_hash1 = svgPanZoom(
            '#image_1', {
                zoomEnabled: true,
                center: true,
                minZoom: 1.0,
                maxZoom: 20,
                controlIconsEnabled: false,
                zoomScaleSensitivity: 0.1,
                fit: false
            }
        );


        document.getElementById('hash1-zoom-in').addEventListener(
            'click', function(ev) {
                ev.preventDefault();
                pan_zoom_hash1.zoomIn();
                console.log("hash1-zoom-in");
            }
        );

        document.getElementById('hash1-zoom-out').addEventListener(
            'click', function(ev) {
                ev.preventDefault();
                pan_zoom_hash1.zoomOut();
                console.log("hash1-zoom-out");
            }
        );

        document.getElementById('hash1-reset').addEventListener(
            'click', function(ev) {
                ev.preventDefault();
                pan_zoom_hash1.resetZoom();
                console.log("hash1-zoom-reset");
            }
        );

        /***************************************************/

        pan_zoom_hash2 = svgPanZoom(
            '#image_2', {
                zoomEnabled: true,
                center: true,
                minZoom: 1.0,
                maxZoom: 20,
                controlIconsEnabled: false,
                zoomScaleSensitivity: 0.1,
                fit: false
            }
        );

        document.getElementById('hash2-zoom-in').addEventListener(
            'click', function(ev) {
                ev.preventDefault();
                pan_zoom_hash2.zoomIn();
                console.log("hash2-zoom-in");
            }
        );

        document.getElementById('hash2-zoom-out').addEventListener(
            'click', function(ev) {
                ev.preventDefault();
                pan_zoom_hash2.zoomOut();
                console.log("hash2-zoom-out");
            }
        );

        document.getElementById('hash2-reset').addEventListener(
            'click', function(ev) {
                ev.preventDefault();
                pan_zoom_hash2.resetZoom();
                console.log("hash2-zoom-reset");
            }
        );

        /***************************************************/

    };

</script>

</body>
</html>
"""

tail = """
<div class="clearfix"></div>
<div style="padding:6px;"></div>
"""
