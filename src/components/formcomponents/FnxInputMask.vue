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
    <div class="fnx-inputmask-wrapper">
      <!-- Input element -->
      <InputMask
        :id="inputId"
        ref="inputRef"
        :model-value="value"
        :mask="mask"
        :auto-clear="autoClear"
        :unmask="unmask"
        :placeholder="placeholder"
        :disabled="disabled || loading"
        :readonly="readonly"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
        @complete="handleComplete"
      />

      <!-- Clear button -->
      <button
        v-if="showClear && value && !disabled && !loading"
        type="button"
        class="fnx-inputmask-clear"
        @click="handleClear"
        :aria-label="'Clear ' + (label || name)"
      >
        <svg viewBox="0 0 20 20" fill="currentColor">
          <path
            fill-rule="evenodd"
            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
            clip-rule="evenodd"
          />
        </svg>
      </button>

      <!-- Loading spinner -->
      <div v-if="loading" class="fnx-inputmask-loading">
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
import { computed, ref, nextTick } from 'vue'
import { useField } from 'vee-validate'
import InputMask from 'primevue/inputmask'
import type { InputMaskProps } from './types/form-types'
import { buildValidationString } from './utils/validation-rules'

// Props
const props = withDefaults(defineProps<InputMaskProps>(), {
  size: 'md',
  modelValue: '',
  mask: '',
  slotChar: '_',
  autoClear: true,
  unmask: false,
  showClear: false
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string]
  'blur': [event: FocusEvent]
  'focus': [event: FocusEvent]
  'input': [event: Event]
  'complete': [event: Event]
  'clear': []
}>()

// Template refs
const inputRef = ref<any>()

// Generate unique ID for the input
const inputId = computed(() => `fnx-inputmask-${props.name}`)

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
    minLength: props.minLength,
    maxLength: props.maxLength
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
  'fnx-inputmask',
  `fnx-inputmask--${props.size}`,
  {
    'fnx-inputmask--error': !!errorMessage.value,
    'fnx-inputmask--success': meta.valid && meta.touched && !errorMessage.value,
    'fnx-inputmask--loading': props.loading,
    'fnx-inputmask--with-clear': props.showClear && value.value
  }
])

// Event handlers
const handleInput = (event: any) => {
  const newValue = event.value || ''
  
  value.value = newValue
  emit('update:modelValue', newValue)
  emit('input', event.originalEvent || event)
  handleChange(event.originalEvent || event)
}

const handleBlur = (event: Event) => {
  veeHandleBlur(event)
  emit('blur', event as FocusEvent)
}

const handleFocus = (event: Event) => {
  emit('focus', event as FocusEvent)
}

const handleComplete = (event: Event) => {
  emit('complete', event)
}

const handleClear = () => {
  value.value = ''
  emit('update:modelValue', '')
  emit('clear')
  
  // Focus the input after clearing
  nextTick(() => {
    const element = inputRef.value?.$el || inputRef.value
    if (element && typeof element.focus === 'function') {
      element.focus()
    }
  })
}

// Public methods (exposed to parent)
const focus = () => {
  const element = inputRef.value?.$el || inputRef.value
  if (element && typeof element.focus === 'function') {
    element.focus()
  }
}

const blur = () => {
  const element = inputRef.value?.$el || inputRef.value
  if (element && typeof element.blur === 'function') {
    element.blur()
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
.fnx-inputmask-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.fnx-inputmask-clear {
  position: absolute;
  right: var(--fnx-spacing-sm);
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--fnx-spacing-xs);
  color: var(--fnx-text-secondary);
  transition: color var(--fnx-transition-duration) var(--fnx-transition-timing);
  z-index: 10;
}

.fnx-inputmask-clear:hover {
  color: var(--fnx-text-primary);
}

.fnx-inputmask-clear svg {
  width: 16px;
  height: 16px;
}

.fnx-inputmask-loading {
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
.fnx-inputmask--sm {
  font-size: var(--fnx-font-size-sm);
}

.fnx-inputmask--lg {
  font-size: var(--fnx-font-size-lg);
}

/* State variants */
.fnx-inputmask--error {
  border-color: var(--fnx-error-500);
}

.fnx-inputmask--success {
  border-color: var(--fnx-success-500);
}

.fnx-inputmask--loading {
  opacity: 0.7;
}

.fnx-inputmask--with-clear {
  padding-right: calc(var(--fnx-spacing-xl) + var(--fnx-spacing-sm));
}
</style>
