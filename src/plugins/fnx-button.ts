// FNX Button Components Plugin
import type { App } from 'vue'
import FnxButton from '../components/buttoncomponents/FnxButton.vue'
import FnxIconButton from '../components/buttoncomponents/FnxIconButton.vue'

// Import component styles
import '../components/buttoncomponents/styles/fnx-button.scss'
import '../components/buttoncomponents/styles/fnx-icon-button.scss'

// Export components for individual imports
export { 
  FnxButton,
  FnxIconButton
}

// Export types
export * from '../components/buttoncomponents/types/button-types'

// Component registry
export const FnxButtonComponents = {
  FnxButton,
  FnxIconButton
}

// Plugin for global registration
export default {
  install(app: App) {
    // Register all button components globally
    Object.entries(FnxButtonComponents).forEach(([name, component]) => {
      app.component(name, component)
    })
  }
}
