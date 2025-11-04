<template>
  <div class="fnx-field" :class="fieldClass">
    <!-- Checkbox wrapper -->
    <div class="fnx-checkbox-wrapper">
      <!-- Checkbox element -->
      <Checkbox
        :id="checkboxId"
        ref="checkboxRef"
        :model-value="value"
        :value="checkboxValue"
        :binary="binary"
        :indeterminate="indeterminate"
        :disabled="disabled || loading"
        :class="checkboxClasses"
        @change="handleChange"
        @blur="handleBlur"
        @focus="handleFocus"
      />

      <!-- Label -->
      <label
        v-if="label"
        :for="checkboxId"
        class="fnx-checkbox-label"
        :class="{ required, disabled: disabled || loading }"
        style="font-size: 0.75rem; font-weight: 400; line-height: 1.4;"
      >
        {{ label }}
      </label>

      <!-- Loading spinner -->
      <div v-if="loading" class="fnx-checkbox-loading">
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
import Checkbox from 'primevue/checkbox'
import type { CheckboxProps } from './types/form-types'
import { buildValidationString } from './utils/validation-rules'

// Props
const props = withDefaults(defineProps<CheckboxProps>(), {
  size: 'md',
  binary: true,
  indeterminate: false
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean | any[]]
  'change': [event: { originalEvent: Event; checked: boolean; value: any }]
  'blur': [event: Event]
  'focus': [event: Event]
}>()

// Template refs
const checkboxRef = ref<any>()

// Generate unique ID for the checkbox
const checkboxId = computed(() => `fnx-checkbox-${props.name}`)

// Determine checkbox value for array binding
const checkboxValue = computed(() => {
  return props.binary ? undefined : props.value
})

// Build validation rules from props
const validationRules = computed(() => {
  // If legacy rules prop is provided, use it
  if (props.rules) {
    return props.rules
  }
  
  // For binary checkboxes, required means must be true
  if (props.binary && props.required) {
    return 'required'
  }
  
  // For array checkboxes, use standard validation
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
  initialValue: props.binary ? (props.modelValue || false) : (props.modelValue || []),
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

const checkboxClasses = computed(() => [
  'fnx-checkbox',
  `fnx-checkbox--${props.size}`,
  {
    'fnx-checkbox--error': !!errorMessage.value,
    'fnx-checkbox--success': meta.valid && meta.touched && !errorMessage.value,
    'fnx-checkbox--loading': props.loading,
    'fnx-checkbox--indeterminate': props.indeterminate
  }
])

// Event handlers
const handleChange = (event: any) => {
  if (props.binary) {
    value.value = event.checked
    emit('update:modelValue', event.checked)
  } else {
    // Handle array binding
    const currentValue = Array.isArray(value.value) ? [...value.value] : []
    if (event.checked) {
      if (!currentValue.includes(props.value)) {
        currentValue.push(props.value)
      }
    } else {
      const index = currentValue.indexOf(props.value)
      if (index > -1) {
        currentValue.splice(index, 1)
      }
    }
    value.value = currentValue
    emit('update:modelValue', currentValue)
  }
  
  emit('change', event)
  veeHandleChange(event.originalEvent)
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
  if (checkboxRef.value) {
    checkboxRef.value.focus()
  }
}

const blur = () => {
  if (checkboxRef.value) {
    checkboxRef.value.blur()
  }
}

// Expose methods to parent component
defineExpose({
  focus,
  blur,
  checkboxRef
})
</script>

<style scoped>
.fnx-checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: var(--fnx-spacing-sm);
  position: relative;
}

.fnx-checkbox-label {
  user-select: none;
  font-size: var(--fnx-font-size-base);
  color: var(--fnx-text-primary);
  transition: color var(--fnx-transition-duration) var(--fnx-transition-timing);
}

.fnx-checkbox-label.required::after {
  content: ' *';
  color: var(--fnx-error-500);
}

.fnx-checkbox-label.disabled {
  cursor: not-allowed;
  opacity: 0.6;
  color: var(--fnx-text-disabled);
}

.fnx-checkbox-loading {
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
.fnx-checkbox--sm {
  transform: scale(0.875);
}

.fnx-checkbox--sm + .fnx-checkbox-label {
  font-size: var(--fnx-font-size-sm);
}

.fnx-checkbox--lg {
  transform: scale(1.125);
}

.fnx-checkbox--lg + .fnx-checkbox-label {
  font-size: var(--fnx-font-size-lg);
}

/* State variants */
.fnx-checkbox--error {
  border-color: var(--fnx-error-500);
}

.fnx-checkbox--success {
  border-color: var(--fnx-success-500);
}

.fnx-checkbox--loading {
  opacity: 0.7;
}

.fnx-checkbox--indeterminate {
  background: var(--fnx-primary-500);
  border-color: var(--fnx-primary-500);
}

/* Custom checkbox styling */
.fnx-checkbox :deep(.p-checkbox-box) {
  border-radius: var(--fnx-border-radius-sm);
  transition: all var(--fnx-transition-duration) var(--fnx-transition-timing);
}

.fnx-checkbox :deep(.p-checkbox-box:hover) {
  border-color: var(--fnx-primary-400);
}

.fnx-checkbox :deep(.p-checkbox-box.p-highlight) {
  background: var(--fnx-primary-500);
  border-color: var(--fnx-primary-500);
}

.fnx-checkbox :deep(.p-checkbox-box.p-highlight:hover) {
  background: var(--fnx-primary-600);
  border-color: var(--fnx-primary-600);
}

.fnx-checkbox--error :deep(.p-checkbox-box) {
  border-color: var(--fnx-error-500);
}

.fnx-checkbox--success :deep(.p-checkbox-box) {
  border-color: var(--fnx-success-500);
}
</style>
