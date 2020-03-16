// Enable JavaScript's strict mode. Strict mode catches some common
// programming errors and throws exceptions, prevents some unsafe actions from
// being taken, and disables some confusing and bad JavaScript features.
"use strict";

this.ckan.module('auto-url-preview-target', {
    initialize: function () {
        var sandbox = this.sandbox;
        var options = this.options;
        var el = this.el;

        sandbox.subscribe('auto-url-preview-created', function (preview) {
            // Append the preview string after the target input.
            el.after(preview);
        });

        // Once the preview box is modified stop watching it.
        sandbox.subscribe('auto-url-preview-modified', function () {
            el.off('.auto-url-preview');
        });

        // Watch for updates to the target field and update the hidden slug field
        // triggering the "change" event manually.
        el.on('keyup.auto-url-preview input.auto-url-preview', function (event) {
            sandbox.publish('auto-url-target-changed', this.value);
            //slug.val(this.value).trigger('change');
        });
    }
});

this.ckan.module('auto-url', function (jQuery) {
  return {
    options: {
      prefix: '',
      placeholder: '<slug>'
    },

    initialize: function () {
      var sandbox = this.sandbox;
      var options = this.options;
      var el = this.el;
      var _ = sandbox.translate;

      var slug = el.slug();
      var parent = slug.parents('.form-group');
      var preview;

      if (!(parent.length)) {
        return;
      }

      // Leave the slug field visible
      if (!parent.hasClass('error')) {
        preview = parent.slugPreview({
          prefix: options.prefix,
          placeholder: options.placeholder,
          i18n: {
            'URL': this._('URL'),
            'Edit': this._('Edit')
          }
        });

        // If the user manually enters text into the input we cancel the slug
        // listeners so that we don't clobber the slug when the title next changes.
        // slug.keypress(function () {
        //   if (event.charCode) {
        //     sandbox.publish('auto-url-preview-modified', preview[0]);
        //   }
        // });

        sandbox.publish('auto-url-preview-created', preview[0]);
      }

      // Watch for updates to the target field and update the hidden slug field
      // triggering the "change" event manually.
      sandbox.subscribe('auto-url-target-changed', function (value) {
        slug.val(value).trigger('change');
      });
    }
  };
})