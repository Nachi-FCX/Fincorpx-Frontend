<template>
  <div class="fnx-field" :class="fieldClass">
    <!-- Label -->
    <label
      v-if="label"
      :for="autocompleteId"
      class="fnx-field-label"
      :class="{ required }"
    >
      {{ label }}
    </label>

    <!-- AutoComplete wrapper -->
    <div class="fnx-autocomplete-wrapper">
      <!-- AutoComplete element -->
      <AutoComplete
        :id="autocompleteId"
        ref="autocompleteRef"
        :model-value="value"
        :suggestions="suggestions"
        :option-label="optionLabel"
        :placeholder="placeholder"
        :disabled="disabled || loading"
        :multiple="multiple"
        :min-length="minLength"
        :delay="delay"
        :dropdown="dropdown"
        :force-selection="forceSelection"
        :empty-message="emptyMessage"
        :class="autocompleteClasses"
        @complete="handleComplete"
        @item-select="handleItemSelect"
        @item-unselect="handleItemUnselect"
        @dropdown-click="handleDropdownClick"
        @clear="handleClear"
        @blur="handleBlur"
        @focus="handleFocus"
      />

      <!-- Loading spinner -->
      <div v-if="loading" class="fnx-autocomplete-loading">
        <div class="fnx-spinner" />
      </div>
    </div>

    <!-- Error message -->
    <div v-if="errorMessage" class="fnx-field-error">
      <svg class="fnx-error-icon" viewBox="0 0 20 20" fill="currentColor">
        <path
          fill-rule="evenodd"
          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
          clip-rule="evenodd"
        />
      </svg>
      {{ errorMessage }}
    </div>

    <!-- Help text -->
    <div v-if="help && !errorMessage" class="fnx-field-help">
      {{ help }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useField } from 'vee-validate'
import AutoComplete from 'primevue/autocomplete'
import type { AutoCompleteProps } from './types/form-types'
import { buildValidationString } from './utils/validation-rules'

// Props
const props = withDefaults(defineProps<AutoCompleteProps>(), {
  size: 'md',
  optionLabel: 'label',
  multiple: false,
  minLength: 1,
  delay: 300,
  dropdown: false,
  forceSelection: false,
  emptyMessage: 'No results found'
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: any]
  'complete': [event: { originalEvent: Event; query: string }]
  'item-select': [event: { originalEvent: Event; value: any }]
  'item-unselect': [event: { originalEvent: Event; value: any }]
  'dropdown-click': [event: { originalEvent: Event; query: string }]
  'clear': []
  'blur': [event: Event]
  'focus': [event: Event]
}>()

// Template refs
const autocompleteRef = ref<any>()

// Generate unique ID for the autocomplete
const autocompleteId = computed(() => `fnx-autocomplete-${props.name}`)

// Build validation rules from props
const validationRules = computed(() => {
  // If legacy rules prop is provided, use it
  if (props.rules) {
    return props.rules
  }
  
  // Build from props
  return buildValidationString({
    required: props.required,
    validationType: props.validationType,
    minLength: props.minLength
  })
})

// VeeValidate integration
const {
  value,
  errorMessage,
  handleBlur: veeHandleBlur,
  handleChange: veeHandleChange,
  meta
} = useField(() => props.name, validationRules, {
  initialValue: props.modelValue,
  syncVModel: true
})

// Computed properties
const fieldClass = computed(() => [
  props.class,
  {
    'fnx-field--error': !!errorMessage.value,
    'fnx-field--success': meta.valid && meta.touched && !errorMessage.value,
    'fnx-field--disabled': props.disabled,
    'fnx-field--loading': props.loading
  }
])

const autocompleteClasses = computed(() => [
  'fnx-autocomplete',
  `fnx-autocomplete--${props.size}`,
  {
    'fnx-autocomplete--error': !!errorMessage.value,
    'fnx-autocomplete--success': meta.valid && meta.touched && !errorMessage.value,
    'fnx-autocomplete--loading': props.loading,
    'fnx-autocomplete--multiple': props.multiple,
    'fnx-autocomplete--dropdown': props.dropdown
  }
])

// Event handlers
const handleComplete = (event: any) => {
  emit('complete', event)
}

const handleItemSelect = (event: any) => {
  value.value = event.value
  emit('update:modelValue', event.value)
  emit('item-select', event)
  veeHandleChange(event.originalEvent || event)
}

const handleItemUnselect = (event: any) => {
  if (props.multiple && Array.isArray(value.value)) {
    const newValue = value.value.filter(item => item !== event.value)
    value.value = newValue
    emit('update:modelValue', newValue)
  } else {
    value.value = null
    emit('update:modelValue', null)
  }
  emit('item-unselect', event)
  veeHandleChange(event.originalEvent || event)
}

const handleDropdownClick = (event: any) => {
  emit('dropdown-click', event)
}

const handleClear = () => {
  value.value = props.multiple ? [] : null
  emit('update:modelValue', value.value)
  emit('clear')
}

const handleBlur = (event: any) => {
  veeHandleBlur(event)
  emit('blur', event)
}

const handleFocus = (event: any) => {
  emit('focus', event)
}

// Public methods (exposed to parent)
const focus = () => {
  if (autocompleteRef.value) {
    autocompleteRef.value.focus()
  }
}

const blur = () => {
  if (autocompleteRef.value) {
    autocompleteRef.value.blur()
  }
}

const show = () => {
  if (autocompleteRef.value) {
    autocompleteRef.value.show()
  }
}

const hide = () => {
  if (autocompleteRef.value) {
    autocompleteRef.value.hide()
  }
}

// Expose methods to parent component
defineExpose({
  focus,
  blur,
  show,
  hide,
  autocompleteRef
})
</script>

<style scoped>
.fnx-autocomplete-wrapper {
  position: relative;
}

.fnx-autocomplete-loading {
  position: absolute;
  right: var(--fnx-spacing-sm);
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.fnx-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--fnx-border-light);
  border-top: 2px solid var(--fnx-primary-500);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Size variants */
.fnx-autocomplete--sm {
  font-size: var(--fnx-font-size-sm);
}

.fnx-autocomplete--lg {
  font-size: var(--fnx-font-size-lg);
}

/* State variants */
.fnx-autocomplete--error {
  border-color: var(--fnx-error-500);
}

.fnx-autocomplete--success {
  border-color: var(--fnx-success-500);
}

.fnx-autocomplete--loading {
  opacity: 0.7;
}

/* Multiple selection styling */
.fnx-autocomplete--multiple :deep(.p-autocomplete-multiple-container) {
  display: flex;
  flex-wrap: wrap;
  gap: var(--fnx-spacing-xs);
  padding: var(--fnx-spacing-xs);
}

.fnx-autocomplete--multiple :deep(.p-autocomplete-token) {
  background: var(--fnx-primary-100);
  color: var(--fnx-primary-700);
  border-radius: var(--fnx-border-radius-sm);
  padding: var(--fnx-spacing-xs) var(--fnx-spacing-sm);
  display: flex;
  align-items: center;
  gap: var(--fnx-spacing-xs);
}

.fnx-autocomplete--multiple :deep(.p-autocomplete-token-icon) {
  color: var(--fnx-primary-600);
  cursor: pointer;
  transition: color var(--fnx-transition-duration) var(--fnx-transition-timing);
}

.fnx-autocomplete--multiple :deep(.p-autocomplete-token-icon:hover) {
  color: var(--fnx-primary-800);
}

/* Dropdown styling */
.fnx-autocomplete--dropdown :deep(.p-autocomplete-dropdown) {
  background: var(--fnx-surface);
  border: 1px solid var(--fnx-border-normal);
  border-left: none;
  color: var(--fnx-text-secondary);
  transition: all var(--fnx-transition-duration) var(--fnx-transition-timing);
}

.fnx-autocomplete--dropdown :deep(.p-autocomplete-dropdown:hover) {
  background: var(--fnx-surface-hover);
  color: var(--fnx-primary-500);
}

/* Custom autocomplete styling */
.fnx-autocomplete :deep(.p-inputtext) {
  border-radius: var(--fnx-border-radius-md);
  transition: all var(--fnx-transition-duration) var(--fnx-transition-timing);
}

.fnx-autocomplete :deep(.p-inputtext:hover) {
  border-color: var(--fnx-primary-400);
}

.fnx-autocomplete :deep(.p-inputtext:focus) {
  outline: 2px solid var(--fnx-primary-200);
  outline-offset: 2px;
  border-color: var(--fnx-primary-500);
}

.fnx-autocomplete--error :deep(.p-inputtext) {
  border-color: var(--fnx-error-500);
}

.fnx-autocomplete--success :deep(.p-inputtext) {
  border-color: var(--fnx-success-500);
}

/* Suggestions panel styling */
.fnx-autocomplete :deep(.p-autocomplete-panel) {
  border-radius: var(--fnx-border-radius-lg);
  box-shadow: var(--fnx-shadow-lg);
  border: 1px solid var(--fnx-border-normal);
  background: var(--fnx-surface);
}

.fnx-autocomplete :deep(.p-autocomplete-items) {
  padding: var(--fnx-spacing-xs);
}

.fnx-autocomplete :deep(.p-autocomplete-item) {
  padding: var(--fnx-spacing-sm) var(--fnx-spacing-md);
  border-radius: var(--fnx-border-radius-sm);
  transition: all var(--fnx-transition-duration) var(--fnx-transition-timing);
  cursor: pointer;
}

.fnx-autocomplete :deep(.p-autocomplete-item:hover) {
  background: var(--fnx-primary-100);
  color: var(--fnx-primary-700);
}

.fnx-autocomplete :deep(.p-autocomplete-item.p-highlight) {
  background: var(--fnx-primary-500);
  color: var(--fnx-text-inverse);
}

.fnx-autocomplete :deep(.p-autocomplete-empty-message) {
  padding: var(--fnx-spacing-md);
  color: var(--fnx-text-secondary);
  text-align: center;
  font-style: italic;
}
</style>
