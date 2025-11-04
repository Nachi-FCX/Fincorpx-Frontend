<template>
  <div class="fnx-field" :class="fieldClass">
    <!-- Radio button wrapper -->
    <div class="fnx-radiobutton-wrapper">
      <!-- RadioButton element -->
      <RadioButton
        :id="radioId"
        ref="radioRef"
        :model-value="value"
        :value="radioValue"
        :disabled="disabled || loading"
        :class="radioClasses"
        @change="handleChange"
        @blur="handleBlur"
        @focus="handleFocus"
      />

      <!-- Label -->
      <label
        v-if="label"
        :for="radioId"
        class="fnx-radiobutton-label"
        :class="{ required, disabled: disabled || loading }"
      >
        {{ label }}
      </label>

      <!-- Loading spinner -->
      <div v-if="loading" class="fnx-radiobutton-loading">
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
import RadioButton from 'primevue/radiobutton'
import type { RadioButtonProps } from './types/form-types'
import { buildValidationString } from './utils/validation-rules'

// Props
const props = withDefaults(defineProps<RadioButtonProps>(), {
  size: 'md'
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: any]
  'change': [event: { originalEvent: Event; value: any }]
  'blur': [event: Event]
  'focus': [event: Event]
}>()

// Template refs
const radioRef = ref<any>()

// Generate unique ID for the radio button
const radioId = computed(() => `fnx-radio-${props.name}-${props.value}`)

// Radio button value
const radioValue = computed(() => props.value)

// Build validation rules from props
const validationRules = computed(() => {
  // If legacy rules prop is provided, use it
  if (props.rules) {
    return props.rules
  }
  
  // Build from props
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

const radioClasses = computed(() => [
  'fnx-radiobutton',
  `fnx-radiobutton--${props.size}`,
  {
    'fnx-radiobutton--error': !!errorMessage.value,
    'fnx-radiobutton--success': meta.valid && meta.touched && !errorMessage.value,
    'fnx-radiobutton--loading': props.loading,
    'fnx-radiobutton--checked': value.value === props.value
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
  if (radioRef.value) {
    radioRef.value.focus()
  }
}

const blur = () => {
  if (radioRef.value) {
    radioRef.value.blur()
  }
}

// Expose methods to parent component
defineExpose({
  focus,
  blur,
  radioRef
})
</script>

<style scoped>
.fnx-radiobutton-wrapper {
  display: flex;
  align-items: center;
  gap: var(--fnx-spacing-sm);
  position: relative;
}

.fnx-radiobutton-label {
  cursor: pointer;
  user-select: none;
  font-size: var(--fnx-font-size-base);
  color: var(--fnx-text-primary);
  transition: color var(--fnx-transition-duration) var(--fnx-transition-timing);
}

.fnx-radiobutton-label.required::after {
  content: ' *';
  color: var(--fnx-error-500);
}

.fnx-radiobutton-label.disabled {
  cursor: not-allowed;
  opacity: 0.6;
  color: var(--fnx-text-disabled);
}

.fnx-radiobutton-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: var(--fnx-spacing-sm);
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
.fnx-radiobutton--sm {
  transform: scale(0.875);
}

.fnx-radiobutton--sm + .fnx-radiobutton-label {
  font-size: var(--fnx-font-size-sm);
}

.fnx-radiobutton--lg {
  transform: scale(1.125);
}

.fnx-radiobutton--lg + .fnx-radiobutton-label {
  font-size: var(--fnx-font-size-lg);
}

/* State variants */
.fnx-radiobutton--error {
  border-color: var(--fnx-error-500);
}

.fnx-radiobutton--success {
  border-color: var(--fnx-success-500);
}

.fnx-radiobutton--loading {
  opacity: 0.7;
}

.fnx-radiobutton--checked {
  background: var(--fnx-primary-500);
  border-color: var(--fnx-primary-500);
}

/* Custom radio button styling */
.fnx-radiobutton :deep(.p-radiobutton-box) {
  transition: all var(--fnx-transition-duration) var(--fnx-transition-timing);
}

.fnx-radiobutton :deep(.p-radiobutton-box:hover) {
  border-color: var(--fnx-primary-400);
}

.fnx-radiobutton :deep(.p-radiobutton-box.p-highlight) {
  background: var(--fnx-primary-500);
  border-color: var(--fnx-primary-500);
}

.fnx-radiobutton :deep(.p-radiobutton-box.p-highlight:hover) {
  background: var(--fnx-primary-600);
  border-color: var(--fnx-primary-600);
}

.fnx-radiobutton :deep(.p-radiobutton-icon) {
  background: var(--fnx-text-inverse);
}

.fnx-radiobutton--error :deep(.p-radiobutton-box) {
  border-color: var(--fnx-error-500);
}

.fnx-radiobutton--success :deep(.p-radiobutton-box) {
  border-color: var(--fnx-success-500);
}

/* Focus styles */
.fnx-radiobutton :deep(.p-radiobutton-box:focus) {
  outline: 2px solid var(--fnx-primary-200);
  outline-offset: 2px;
}
</style>
