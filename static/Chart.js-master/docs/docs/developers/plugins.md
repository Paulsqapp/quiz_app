---
title: Plugins
---
import useBaseUrl from '@docusaurus/useBaseUrl';

Plugins are the most efficient way to customize or change the default behavior of a chart. They have been introduced at [version 2.1.0](https://github.com/chartjs/Chart.js/releases/tag/2.1.0) (global plugins only) and extended at [version 2.5.0](https://github.com/chartjs/Chart.js/releases/tag/v2.5.0) (per chart plugins and options).

## Using plugins

Plugins can be shared between chart instances:

```javascript
var plugin = { /* plugin implementation */ };

// chart1 and chart2 use "plugin"
var chart1 = new Chart(ctx, {
    plugins: [plugin]
});

var chart2 = new Chart(ctx, {
    plugins: [plugin]
});

// chart3 doesn't use "plugin"
var chart3 = new Chart(ctx, {});
```

Plugins can also be defined directly in the chart `plugins` config (a.k.a. *inline plugins*):

> Note: *inline* plugins are not registered. Some plugins require registering, i.e. can't be used *inline*.

```javascript
var chart = new Chart(ctx, {
    plugins: [{
        beforeInit: function(chart, args, options) {
            //..
        }
    }]
});
```

However, this approach is not ideal when the customization needs to apply to many charts.

## Global plugins

Plugins can be registered globally to be applied on all charts (a.k.a. *global plugins*):

```javascript
Chart.register({
    // plugin implementation
});
```

> Note: *inline* plugins can't be registered globally.

## Configuration

### Plugin ID

Plugins must define a unique id in order to be configurable.

This id should follow the [npm package name convention](https://docs.npmjs.com/files/package.json#name):

- can't start with a dot or an underscore
- can't contain any non-URL-safe characters
- can't contain uppercase letters
- should be something short, but also reasonably descriptive

If a plugin is intended to be released publicly, you may want to check the [registry](https://www.npmjs.com/search?q=chartjs-plugin-) to see if there's something by that name already. Note that in this case, the package name should be prefixed by `chartjs-plugin-` to appear in Chart.js plugin registry.

### Plugin options

Plugin options are located under the `options.plugins` config and are scoped by the plugin ID: `options.plugins.{plugin-id}`.

```javascript
var chart = new Chart(ctx, {
    options: {
        foo: { ... },           // chart 'foo' option
        plugins: {
            p1: {
                foo: { ... },   // p1 plugin 'foo' option
                bar: { ... }
            },
            p2: {
                foo: { ... },   // p2 plugin 'foo' option
                bla: { ... }
            }
        }
    }
});
```

#### Disable plugins

To disable a global plugin for a specific chart instance, the plugin options must be set to `false`:

```javascript
Chart.register({
    id: 'p1',
    // ...
});

var chart = new Chart(ctx, {
    options: {
        plugins: {
            p1: false   // disable plugin 'p1' for this instance
        }
    }
});
```

To disable all plugins for a specific chart instance, set `options.plugins` to `false`:

```javascript
var chart = new Chart(ctx, {
    options: {
        plugins: false // all plugins are disabled for this instance
    }
});
```

## Plugin Core API

Read more about the [existing plugin extension hooks](https://github.com/chartjs/Chart.js/blob/master/types/index.esm.d.ts#L733).

### Chart Initialization

Plugins are notified during the initialization process. These hooks can be used to setup data needed for the plugin to operate.

<img alt="Chart.js init flowchart" src={useBaseUrl('img/init_flowchart.png')} />

### Chart Update

Plugins are notified during throughout the update process.

<img alt="Chart.js update flowchart" src={useBaseUrl('img/update_flowchart.png')} />

### Rendering

Plugins can interact with the chart throughout the render process. The rendering process is documented in the flowchart below. Each of the green processes is a plugin notification. The red lines indicate how cancelling part of the render process can occur when a plugin returns `false` from a hook. Not all hooks are cancelable, however, in general most `before*` hooks can be cancelled.

<img alt="Chart.js render pipeline flowchart" src={useBaseUrl('img/render_flowchart.png')} />
