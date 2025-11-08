/**
 * Leaflet Heat Canvas Patch
 * Fixes the Canvas2D performance warning by setting willReadFrequently attribute
 * This patch overrides the canvas context creation to optimize for frequent readback operations
 * 
 * Background:
 * leaflet.heat uses getImageData frequently for heatmap rendering.
 * Modern browsers show warnings when getImageData is called repeatedly without
 * the willReadFrequently flag, as it affects GPU optimization strategies.
 * 
 * This patch adds willReadFrequently: true to all 2D canvas contexts,
 * eliminating the console warning and improving performance.
 */

let patchApplied = false;

// Store the original getContext method
const originalGetContext = HTMLCanvasElement.prototype.getContext;

export default function applyLeafletHeatPatch() {
  // Only apply patch once
  if (patchApplied) {
    return;
  }

  // Override getContext to add willReadFrequently for 2d contexts
  HTMLCanvasElement.prototype.getContext = function(contextType, contextAttributes) {
    // Only apply patch for 2d context used by leaflet-heat and similar libraries
    if (contextType === '2d') {
      // Merge with existing attributes or create new object
      const enhancedAttributes = {
        ...(contextAttributes || {}),
        willReadFrequently: true
      };
      return originalGetContext.call(this, contextType, enhancedAttributes);
    }
    
    // For other context types (webgl, etc), use original method
    return originalGetContext.call(this, contextType, contextAttributes);
  };

  patchApplied = true;
  console.log('✅ Canvas2D performance patch applied - willReadFrequently enabled for all 2D contexts');
}
