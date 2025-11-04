// FNX Form Components Plugin
import type { App } from 'vue'
import FnxInputtext from '../components/formcomponents/FnxInputtext.vue'
import FnxDropdown from '../components/formcomponents/FnxDropdown.vue'
import FnxInputNumber from '../components/formcomponents/FnxInputNumber.vue'
import FnxPassword from '../components/formcomponents/FnxPassword.vue'
import FnxTextarea from '../components/formcomponents/FnxTextarea.vue'
import FnxMultiSelect from '../components/formcomponents/FnxMultiSelect.vue'
import FnxCheckbox from '../components/formcomponents/FnxCheckbox.vue'
import FnxRadioButton from '../components/formcomponents/FnxRadioButton.vue'
import FnxToggleButton from '../components/formcomponents/FnxToggleButton.vue'
import FnxCalendar from '../components/formcomponents/FnxCalendar.vue'
import FnxAutoComplete from '../components/formcomponents/FnxAutoComplete.vue'
import FnxInputMask from '../components/formcomponents/FnxInputMask.vue'

// Import component styles
import '../components/formcomponents/styles/fnx-inputtext.scss'
import '../components/formcomponents/styles/fnx-dropdown.scss'

// Export components for individual imports
export { 
  FnxInputtext, 
  FnxDropdown, 
  FnxInputNumber, 
  FnxPassword, 
  FnxTextarea,
  FnxMultiSelect,
  FnxCheckbox,
  FnxRadioButton,
  FnxToggleButton,
  FnxCalendar,
  FnxAutoComplete,
  FnxInputMask
}

// Export types
export * from '../components/formcomponents/types/form-types'

// Component registry
export const FnxFormComponents = {
  FnxInputtext,
  FnxDropdown,
  FnxInputNumber,
  FnxPassword,
  FnxTextarea,
  FnxMultiSelect,
  FnxCheckbox,
  FnxRadioButton,
  FnxToggleButton,
  FnxCalendar,
  FnxAutoComplete,
  FnxInputMask
}

// Plugin for global registration
export default {
  install(app: App) {
    // Register all form components globally
    Object.entries(FnxFormComponents).forEach(([name, component]) => {
      app.component(name, component)
    })
  }
}
