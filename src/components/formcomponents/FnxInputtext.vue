<template>
  <div class="fnx-field" :class="fieldClass">
    <!-- Label -->
    <div v-if="label || $slots.labelSuffix" class="fnx-field-label-wrapper" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.25rem;">
      <label
        v-if="label"
        :for="inputId"
        class="fnx-field-label"
        :class="{ required }"
        style="font-size: 0.75rem; font-weight: 500;"
      >
        {{ label }}
      </label>
      <slot name="labelSuffix" />
    </div>

    <!-- Input wrapper -->
    <div class="fnx-inputtext-wrapper">
      <!-- Prefix icon -->
      <div
        v-if="prefixIcon"
        class="fnx-inputtext-icon fnx-inputtext-icon--prefix"
      >
        <component :is="prefixIcon" v-if="typeof prefixIcon !== 'string'" />
        <i v-else :class="prefixIcon" />
      </div>

      <!-- Input element -->
      <InputText
        :id="inputId"
        ref="inputRef"
        :model-value="value"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled || loading"
        :maxlength="maxlength"
        :minlength="minlength"
        :pattern="pattern"
        :autocomplete="autocomplete"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
        @keydown="handleKeydown"
      />

      <!-- Suffix icon -->
      <div
        v-if="suffixIcon && !clearable && !loading"
        class="fnx-inputtext-icon fnx-inputtext-icon--suffix"
      >
        <component :is="suffixIcon" v-if="typeof suffixIcon !== 'string'" />
        <i v-else :class="suffixIcon" />
      </div>

      <!-- Clear button -->
      <button
        v-if="clearable && value && !disabled && !loading"
        type="button"
        class="fnx-inputtext-clear"
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
      <div v-if="loading" class="fnx-inputtext-loading">
        <div class="fnx-spinner" />
      </div>
    </div>

    <!-- Character counter -->
    <div
      v-if="showCounter && maxlength"
      class="fnx-inputtext-counter"
      :class="{ 'fnx-inputtext-counter--over-limit': isOverLimit }"
    >
      {{ characterCount }}/{{ maxlength }}
    </div>

    <!-- Error message -->
    <div v-if="displayErrorMessage" class="fnx-field-error">
      <svg class="fnx-error-icon" viewBox="0 0 20 20" fill="currentColor">
        <path
          fill-rule="evenodd"
          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
          clip-rule="evenodd"
        />
      </svg>
      {{ displayErrorMessage }}
    </div>

    <!-- Help text -->
    <div v-if="help && !displayErrorMessage" class="fnx-field-help">
      {{ help }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick, onMounted } from 'vue'
import { useField } from 'vee-validate'
import InputText from 'primevue/inputtext'
import type { InputTextProps } from './types/form-types'
import { buildValidationString } from './utils/validation-rules'

// Props
const props = withDefaults(defineProps<InputTextProps>(), {
  type: 'text',
  size: 'md',
  modelValue: '',
  autocomplete: 'off',
  autofocus: false,
  focusOnMount: false,
  textTransform: 'none'
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string]
  'blur': [event: FocusEvent]
  'focus': [event: FocusEvent]
  'input': [event: Event]
  'change': [event: Event]
  'clear': []
}>()

// Template refs
const inputRef = ref<any>()

// Generate unique ID for the input
const inputId = computed(() => `fnx-input-${props.name}`)

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
const characterCount = computed(() => (value.value || '').length)
const isOverLimit = computed(() => props.maxlength ? characterCount.value > props.maxlength : false)

// Combined error message - prioritize manual error prop over VeeValidate error
const displayErrorMessage = computed(() => props.error || errorMessage.value)

const fieldClass = computed(() => [
  props.class,
  {
    'fnx-field--error': !!displayErrorMessage.value,
    'fnx-field--success': meta.valid && meta.touched && !displayErrorMessage.value && !props.error,
    'fnx-field--disabled': props.disabled,
    'fnx-field--loading': props.loading
  }
])

const inputClasses = computed(() => [
  'fnx-inputtext',
  `fnx-inputtext--${props.size}`,
  {
    'fnx-inputtext--error': !!displayErrorMessage.value,
    'fnx-inputtext--success': meta.valid && meta.touched && !displayErrorMessage.value && !props.error,
    'fnx-inputtext--loading': props.loading,
    'fnx-inputtext--with-prefix': !!props.prefixIcon,
    'fnx-inputtext--with-suffix': !!props.suffixIcon || props.clearable || props.loading
  }
])

// Text transformation utility
const applyTextTransform = (text: string): string => {
  switch (props.textTransform) {
    case 'uppercase':
      return text.toUpperCase()
    case 'lowercase':
      return text.toLowerCase()
    case 'capitalize':
      return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase()
    case 'none':
    default:
      return text
  }
}

// Event handlers
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  let newValue = target.value
  
  // Apply text transformation
  if (props.textTransform && props.textTransform !== 'none') {
    const transformedValue = applyTextTransform(newValue)
    
    // Update the input element's value to show the transformed text
    if (transformedValue !== newValue) {
      const cursorPosition = target.selectionStart || 0
      target.value = transformedValue
      
      // Restore cursor position
      nextTick(() => {
        target.setSelectionRange(cursorPosition, cursorPosition)
      })
    }
    
    newValue = transformedValue
  }
  
  value.value = newValue
  emit('update:modelValue', newValue)
  emit('input', event)
  handleChange(event)
}

const handleBlur = (event: FocusEvent) => {
  veeHandleBlur(event)
  emit('blur', event)
}

const handleFocus = (event: FocusEvent) => {
  emit('focus', event)
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.clearable && value.value) {
    handleClear()
  }
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

// Auto-focus functionality
const handleAutoFocus = async () => {
  if (props.autofocus || props.focusOnMount) {
    await nextTick()
    focus()
  }
}

// Public methods (exposed to parent)
const focus = () => {
  nextTick(() => {
    const element = inputRef.value?.$el || inputRef.value
    if (element && typeof element.focus === 'function') {
      element.focus()
    }
  })
}

const blur = () => {
  const element = inputRef.value?.$el || inputRef.value
  if (element && typeof element.blur === 'function') {
    element.blur()
  }
}

const select = () => {
  const element = inputRef.value?.$el || inputRef.value
  if (element && typeof element.select === 'function') {
    element.select()
  }
}

// Lifecycle hooks
onMounted(() => {
  handleAutoFocus()
})

// Expose methods to parent component
defineExpose({
  focus,
  blur,
  select,
  inputRef
})
</script>
