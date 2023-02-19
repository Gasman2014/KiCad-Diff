
var keysDown = {};

var pan_zoom_diff;
var pan_zoom_hash1;
var pan_zoom_hash2;


function toFixed(value, precision)
{
    var power = Math.pow(10, precision || 0);
    return String(Math.round(value * power) / power);
}

function setCookie(cname, cvalue, exdays)
{
    const d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname)
{
    name = cname + "=";
    decodedCookie = decodeURIComponent(document.cookie);
    ca = decodedCookie.split(';');
    for (i = 0; i < ca.length; i++)
    {
        c = ca[i];
        while (c.charAt(0) == ' ') {
            {
                c = c.substring(1);
            }
        }
        if (c.indexOf(name) == 0) {
            {
                return c.substring(name.length, c.length);
            }
        }
    }
    return "";
}

function save_svg_pan_zoom_settings(pan_zoom_oject, cname_base)
{
    panx   = pan_zoom_oject.getPan().x;
    pany   = pan_zoom_oject.getPan().y;
    width  = pan_zoom_oject.getSizes().width;
    height = pan_zoom_oject.getSizes().height;
    zoom   = pan_zoom_oject.getSizes().realZoom;

    // console.log(toFixed(width, 2), toFixed(height, 2), toFixed(zoom, 2), toFixed(panx, 2), toFixed(pany, 2));

    setCookie(cname_base + "_panx",   panx,   1);
    setCookie(cname_base + "_pany",   pany,   1);
    setCookie(cname_base + "_width",  width,  1);
    setCookie(cname_base + "_height", height, 1);
    setCookie(cname_base + "_zoom",   zoom,   1);

    return {panx, pany, width, height, zoom}
}

function retrieve_svg_pan_zoom_settings(pan_zoom_oject, cname_base)
{
    panx   = getCookie(cname_base + "_panx");
    pany   = getCookie(cname_base + "_pany");
    width  = getCookie(cname_base + "_width");
    height = getCookie(cname_base + "_height");
    zoom   = getCookie(cname_base + "_zoom");

    // console.log(toFixed(width, 2), toFixed(height, 2), toFixed(zoom, 2), toFixed(panx, 2), toFixed(pany, 2));

    if (panx === undefined || panx === null) {
        panx = pan_zoom_oject.getPan().x;
    }

    if (pany === undefined || panx === null) {
        pany = pan_zoom_oject.getPan().y;
    }

    if (width === undefined || panx === null) {
        width = pan_zoom_oject.getSizes().width;
    }

    if (height === undefined || panx === null) {
        height = pan_zoom_oject.getSizes().height;
    }

    if (zoom === undefined || panx === null) {
        zoom = pan_zoom_oject.getSizes().realZoom;
    }

    pan_zoom_oject.zoom(zoom);
    pan_zoom_oject.pan({x: panx, y: pany});

    return {panx, pany, width, height, zoom}
}

window.onkeydown = function(e)
{
    keysDown[e.key] = true;

    if (keysDown.ArrowLeft)
    {
        keysDown = {};
        document.location.href = previous_page; // this variable is in the html
    }

    if (keysDown.ArrowRight)
    {
        keysDown = {};
        document.location.href = next_page; // this variable is in the html
    }

    if (keysDown.h || keysDown.H || e.which === 32) {
        keysDown = {};
        document.location.href = homepage;
    }

    if (keysDown.f || keysDown.F) {
        keysDown = {};
        pan_zoom_diff.resetZoom();
        pan_zoom_diff.center();
        pan_zoom_hash1.resetZoom();
        pan_zoom_hash1.center();
        pan_zoom_hash2.resetZoom();
        pan_zoom_hash2.center();
    }

    if (keysDown.ArrowUp || event.key === ']')
    {
        keysDown = {};

        tabs = $("input:radio[name='tabbed']");
        selected_tab = tabs.index(tabs.filter(':checked'));

        new_index = selected_tab + 1;
        if (new_index >= tabs.length) {
            new_index = 0;
        }

        tabs[new_index].checked = true;
    }

    if (keysDown.ArrowDown || event.key === '[')
    {
        keysDown = {};

        tabs = $("input:radio[name='tabbed']");
        selected_tab = tabs.index(tabs.filter(':checked'));

        new_index = selected_tab - 1;
        if (new_index < 0) {
            new_index = tabs.length-1;
        }

        tabs[new_index].checked = true;
    }

};

window.onload = function()
{
    document.getElementById('svg-compo-diff').style.display = "none";
    document.getElementById('hash1_image').style.display = "none";
    document.getElementById('hash2_image').style.display = "none";

    pan_zoom_diff = svgPanZoom(
        '#svg-compo-diff', {
            zoomEnabled: true,
            controlIconsEnabled: false,
            //center: true,
            minZoom: 1,
            maxZoom: 20,
            zoomScaleSensitivity: 0.1,
            fit: false,
            viewportSelector: '.svg-pan-zoom_diff-viewport',
            eventsListenerElement: document.querySelector('#svg-compo-diff .svg-pan-zoom_diff-viewport')
        }
    );

    document.getElementById('diff-zoom-in').addEventListener(
        'click', function(ev) {
            ev.preventDefault();
            pan_zoom_diff.zoomIn();
        }
    );

    document.getElementById('diff-zoom-out').addEventListener(
        'click', function(ev) {
            ev.preventDefault();
            pan_zoom_diff.zoomOut();
        }
    );

    document.getElementById('diff-reset').addEventListener(
        'click', function(ev) {
            ev.preventDefault();
            pan_zoom_diff.resetZoom();
            pan_zoom_diff.center();
        }
    );

    retrieve_svg_pan_zoom_settings(pan_zoom_diff, "pan_zoom_diff");

    pan_zoom_diff.setOnZoom(function(level)
    {
        save_svg_pan_zoom_settings(pan_zoom_diff, "pan_zoom_diff");
    });

    pan_zoom_diff.setOnPan(function(point){
        save_svg_pan_zoom_settings(pan_zoom_diff, "pan_zoom_diff");
    });


    //==========================================================

    pan_zoom_hash1 = svgPanZoom(
        '#hash1_image', {
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
        }
    );

    document.getElementById('hash1-zoom-out').addEventListener(
        'click', function(ev) {
            ev.preventDefault();
            pan_zoom_hash1.zoomOut();
        }
    );

    document.getElementById('hash1-reset').addEventListener(
        'click', function(ev) {
            ev.preventDefault();
            pan_zoom_hash1.resetZoom();
        }
    );

    retrieve_svg_pan_zoom_settings(pan_zoom_hash1, "pan_zoom_hash1");

    pan_zoom_hash1.setOnZoom(function(level)
    {
        pan_zoom_hash2.zoom(level);
        pan_zoom_hash2.pan(pan_zoom_hash1.getPan());
        save_svg_pan_zoom_settings(pan_zoom_hash1, "pan_zoom_hash1");
    });

    pan_zoom_hash1.setOnPan(function(point)
    {
        pan_zoom_hash2.pan(point);
        save_svg_pan_zoom_settings(pan_zoom_hash1, "pan_zoom_hash1");
    });


    //==========================================================

    pan_zoom_hash2 = svgPanZoom(
        '#hash2_image', {
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
        }
    );

    document.getElementById('hash2-zoom-out').addEventListener(
        'click', function(ev) {
            ev.preventDefault();
            pan_zoom_hash2.zoomOut();
        }
    );

    document.getElementById('hash2-reset').addEventListener(
        'click', function(ev) {
            ev.preventDefault();
            pan_zoom_hash2.resetZoom();
        }
    );

    retrieve_svg_pan_zoom_settings(pan_zoom_hash2, "pan_zoom_hash2");

    pan_zoom_hash2.setOnZoom(function(level)
    {
        pan_zoom_hash1.zoom(level);
        pan_zoom_hash1.pan(pan_zoom_hash2.getPan());
        save_svg_pan_zoom_settings(pan_zoom_hash2, "pan_zoom_hash2");
    });

    pan_zoom_hash2.setOnPan(function(point)
    {
        pan_zoom_hash1.pan(point);
        save_svg_pan_zoom_settings(pan_zoom_hash2, "pan_zoom_hash2");
    });


    //===========================

    document.getElementById('svg-compo-diff').style.display = "inline";
    document.getElementById('hash1_image').style.display = "inline";
    document.getElementById('hash2_image').style.display = "inline";

};

// Hide fields with missing images
function imgError(image_id)
{
    // image.onerror = null;
    console.log("ID", image_id)
    document.getElementById(image_id).onerror = null;
    document.getElementById(image_id).style.display = "none";
    return true;
}
