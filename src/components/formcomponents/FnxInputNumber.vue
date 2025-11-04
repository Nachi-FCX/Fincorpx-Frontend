<template>
  <div class="fnx-field" :class="fieldClass">
    <!-- Label -->
    <label
      v-if="label"
      :for="inputId"
      class="fnx-field-label"
      :class="{ required }"
    >
      {{ label }}
    </label>

    <!-- Input wrapper -->
    <div class="fnx-inputnumber-wrapper">
      <!-- Prefix -->
      <div v-if="prefix" class="fnx-inputnumber-prefix">
        {{ prefix }}
      </div>

      <!-- InputNumber element -->
      <InputNumber
        :id="inputId"
        ref="inputRef"
        :model-value="value"
        :placeholder="placeholder"
        :disabled="disabled || loading"
        :min="min"
        :max="max"
        :step="step"
        :min-fraction-digits="fractionDigits"
        :max-fraction-digits="fractionDigits"
        :allow-empty="!required"
        :show-buttons="showButtons"
        :button-layout="buttonLayout"
        :prefix="prefix"
        :suffix="suffix"
        :currency="currency"
        :locale="locale"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
      />

      <!-- Suffix -->
      <div v-if="suffix" class="fnx-inputnumber-suffix">
        {{ suffix }}
      </div>

      <!-- Loading spinner -->
      <div v-if="loading" class="fnx-inputnumber-loading">
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
import InputNumber from 'primevue/inputnumber'
import type { InputNumberProps } from './types/form-types'
import { buildValidationString } from './utils/validation-rules'

// Props
const props = withDefaults(defineProps<InputNumberProps>(), {
  size: 'md',
  step: 1,
  fractionDigits: 0,
  allowDecimal: true,
  allowNegative: true,
  showButtons: false,
  buttonLayout: 'stacked',
  locale: 'en-US'
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: number | null]
  'blur': [event: Event]
  'focus': [event: Event]
  'input': [event: any]
}>()

// Template refs
const inputRef = ref<any>()

// Generate unique ID for the input
const inputId = computed(() => `fnx-inputnumber-${props.name}`)

// Build validation rules from props
const validationRules = computed(() => {
  // If legacy rules prop is provided, use it
  if (props.rules) {
    return props.rules
  }
  
  // Otherwise build from props
  return buildValidationString({
    required: props.required,
    validationType: props.validationType,
    min: props.min,
    max: props.max
  })
})

// VeeValidate integration
const {
  value,
  errorMessage,
  handleBlur: veeHandleBlur,
  handleChange,
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

const inputClasses = computed(() => [
  'fnx-inputnumber',
  `fnx-inputnumber--${props.size}`,
  {
    'fnx-inputnumber--error': !!errorMessage.value,
    'fnx-inputnumber--success': meta.valid && meta.touched && !errorMessage.value,
    'fnx-inputnumber--loading': props.loading,
    'fnx-inputnumber--with-buttons': props.showButtons,
    'fnx-inputnumber--with-prefix': !!props.prefix,
    'fnx-inputnumber--with-suffix': !!props.suffix
  }
])

// Event handlers
const handleInput = (event: any) => {
  const newValue = event.value
  value.value = newValue
  emit('update:modelValue', newValue)
  emit('input', event)
  handleChange(event.originalEvent || event)
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
  if (inputRef.value) {
    inputRef.value.focus()
  }
}

const blur = () => {
  if (inputRef.value) {
    inputRef.value.blur()
  }
}

// Expose methods to parent component
defineExpose({
  focus,
  blur,
  inputRef
})
</script>

<style scoped>
.fnx-inputnumber-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.fnx-inputnumber-prefix,
.fnx-inputnumber-suffix {
  padding: 0 var(--fnx-spacing-sm);
  color: var(--fnx-text-secondary);
  font-size: var(--fnx-font-size-sm);
  white-space: nowrap;
}

.fnx-inputnumber-loading {
  position: absolute;
  right: var(--fnx-spacing-sm);
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
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
.fnx-inputnumber--sm {
  font-size: var(--fnx-font-size-sm);
}

.fnx-inputnumber--lg {
  font-size: var(--fnx-font-size-lg);
}

/* State variants */
.fnx-inputnumber--error {
  border-color: var(--fnx-error-500);
}

.fnx-inputnumber--success {
  border-color: var(--fnx-success-500);
}

.fnx-inputnumber--loading {
  opacity: 0.7;
}
</style>
