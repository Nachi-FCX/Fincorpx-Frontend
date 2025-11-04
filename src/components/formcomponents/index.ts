// Form Components Export
export { default as FnxInputtext } from './FnxInputtext.vue'
export { default as FnxPassword } from './FnxPassword.vue'
export { default as FnxTextarea } from './FnxTextarea.vue'
export { default as FnxInputNumber } from './FnxInputNumber.vue'
export { default as FnxDropdown } from './FnxDropdown.vue'
export { default as FnxMultiSelect } from './FnxMultiSelect.vue'
export { default as FnxAutoComplete } from './FnxAutoComplete.vue'
export { default as FnxCalendar } from './FnxCalendar.vue'
export { default as FnxCheckbox } from './FnxCheckbox.vue'
export { default as FnxRadioButton } from './FnxRadioButton.vue'
export { default as FnxToggleButton } from './FnxToggleButton.vue'
export { default as FnxInputMask } from './FnxInputMask.vue'
export { default as FnxOtp } from './FnxOtp.vue'

// Form Components Types Export
export type {
  BaseFieldProps,
  InputTextProps,
  PasswordProps,
  TextareaProps,
  InputNumberProps,
  DropdownProps,
  DropdownOption,
  MultiSelectProps,
  AutoCompleteProps,
  CalendarProps,
  FileUploadProps,
  CheckboxProps,
  RadioButtonProps,
  ToggleButtonProps,
  SliderProps,
  RatingProps,
  InputMaskProps,
  ColorPickerProps,
  ButtonProps,
  OtpProps,
  OtpEvents,
  ValidationState,
  FormFieldEvents,
  DropdownEvents,
  ThemeMode,
  ComponentSize,
  ComponentVariant,
  MaybeRef,
  MaybeRefOrGetter
} from './types/form-types'

// Validation utilities export
export { buildValidationString, calculatePasswordStrength } from './utils/validation-rules'
