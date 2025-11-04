// FNX Data Components Plugin
import type { App } from 'vue'
import FnxDataTable from '../components/datacomponents/FnxDataTable.vue'
import LanguageSwitcher from '../components/datacomponents/LanguageSwitcher.vue'

// Import component styles
import '../components/datacomponents/styles/fnx-datatable.scss'

// Export components for individual imports
export { 
  FnxDataTable,
  LanguageSwitcher
}

// Export types
export * from '../components/datacomponents/types/datatable-types'

// Component registry
export const FnxDataComponents = {
  FnxDataTable,
  LanguageSwitcher
}

// Plugin for global registration
export default {
  install(app: App) {
    // Register all data components globally
    Object.entries(FnxDataComponents).forEach(([name, component]) => {
      app.component(name, component)
    })
  }
}
