<template>
  <div class="fnx-field" :class="fieldClass">
    <!-- Label -->
    <label
      v-if="label"
      :for="toggleId"
      class="fnx-field-label"
      :class="{ required }"
    >
      {{ label }}
    </label>

    <!-- ToggleButton wrapper -->
    <div class="fnx-togglebutton-wrapper">
      <!-- ToggleButton element -->
      <ToggleButton
        :id="toggleId"
        ref="toggleRef"
        :model-value="value"
        :on-label="onLabel"
        :off-label="offLabel"
        :on-icon="onIcon"
        :off-icon="offIcon"
        :disabled="disabled || loading"
        :class="toggleClasses"
        @change="handleChange"
        @blur="handleBlur"
        @focus="handleFocus"
      />

      <!-- Loading spinner -->
      <div v-if="loading" class="fnx-togglebutton-loading">
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
import ToggleButton from 'primevue/togglebutton'
import type { ToggleButtonProps } from './types/form-types'
import { buildValidationString } from './utils/validation-rules'

// Props
const props = withDefaults(defineProps<ToggleButtonProps>(), {
  size: 'md',
  onLabel: 'On',
  offLabel: 'Off',
  onIcon: 'pi pi-check',
  offIcon: 'pi pi-times'
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'change': [event: { originalEvent: Event; value: boolean }]
  'blur': [event: Event]
  'focus': [event: Event]
}>()

// Template refs
const toggleRef = ref<any>()

// Generate unique ID for the toggle button
const toggleId = computed(() => `fnx-togglebutton-${props.name}`)

// Build validation rules from props
const validationRules = computed(() => {
  // If legacy rules prop is provided, use it
  if (props.rules) {
    return props.rules
  }
  
  // For toggle buttons, required means must be true
  if (props.required) {
    return 'required'
  }
  
  return buildValidationString({
    required: props.required,
    validationType: props.validationType
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
  initialValue: props.modelValue || false,
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

const toggleClasses = computed(() => [
  'fnx-togglebutton',
  `fnx-togglebutton--${props.size}`,
  {
    'fnx-togglebutton--error': !!errorMessage.value,
    'fnx-togglebutton--success': meta.valid && meta.touched && !errorMessage.value,
    'fnx-togglebutton--loading': props.loading,
    'fnx-togglebutton--on': value.value
  }
])

// Event handlers
const handleChange = (event: any) => {
  value.value = event.value
  emit('update:modelValue', event.value)
  emit('change', event)
  veeHandleChange(event.originalEvent || event)
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
  if (toggleRef.value) {
    toggleRef.value.focus()
  }
}

const blur = () => {
  if (toggleRef.value) {
    toggleRef.value.blur()
  }
}

// Expose methods to parent component
defineExpose({
  focus,
  blur,
  toggleRef
})
</script>

<style scoped>
.fnx-togglebutton-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.fnx-togglebutton-loading {
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
  width: 14px;
  height: 14px;
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
.fnx-togglebutton--sm {
  font-size: var(--fnx-font-size-sm);
  padding: var(--fnx-spacing-xs) var(--fnx-spacing-sm);
}

.fnx-togglebutton--lg {
  font-size: var(--fnx-font-size-lg);
  padding: var(--fnx-spacing-md) var(--fnx-spacing-lg);
}

/* State variants */
.fnx-togglebutton--error {
  border-color: var(--fnx-error-500);
}

.fnx-togglebutton--success {
  border-color: var(--fnx-success-500);
}

.fnx-togglebutton--loading {
  opacity: 0.7;
}

.fnx-togglebutton--on {
  background: var(--fnx-primary-500);
  border-color: var(--fnx-primary-500);
  color: var(--fnx-text-inverse);
}

/* Custom toggle button styling */
.fnx-togglebutton :deep(.p-togglebutton) {
  border-radius: var(--fnx-border-radius-md);
  transition: all var(--fnx-transition-duration) var(--fnx-transition-timing);
  font-weight: var(--fnx-font-weight-medium);
}

.fnx-togglebutton :deep(.p-togglebutton:hover) {
  border-color: var(--fnx-primary-400);
}

.fnx-togglebutton :deep(.p-togglebutton.p-highlight) {
  background: var(--fnx-primary-500);
  border-color: var(--fnx-primary-500);
  color: var(--fnx-text-inverse);
}

.fnx-togglebutton :deep(.p-togglebutton.p-highlight:hover) {
  background: var(--fnx-primary-600);
  border-color: var(--fnx-primary-600);
}

.fnx-togglebutton--error :deep(.p-togglebutton) {
  border-color: var(--fnx-error-500);
}

.fnx-togglebutton--success :deep(.p-togglebutton) {
  border-color: var(--fnx-success-500);
}

/* Focus styles */
.fnx-togglebutton :deep(.p-togglebutton:focus) {
  outline: 2px solid var(--fnx-primary-200);
  outline-offset: 2px;
}

/* Icon spacing */
.fnx-togglebutton :deep(.p-togglebutton .p-button-icon) {
  margin-right: var(--fnx-spacing-xs);
}

.fnx-togglebutton :deep(.p-togglebutton .p-button-icon:last-child) {
  margin-right: 0;
  margin-left: var(--fnx-spacing-xs);
}

/* Disabled state */
.fnx-togglebutton :deep(.p-togglebutton:disabled) {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
