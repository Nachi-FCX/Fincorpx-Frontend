<template>
  <div class="fnx-field" :class="fieldClass">
    <!-- Label -->
    <label
      v-if="label"
      :for="textareaId"
      class="fnx-field-label"
      :class="{ required }"
    >
      {{ label }}
    </label>

    <!-- Textarea wrapper -->
    <div class="fnx-textarea-wrapper">
      <!-- Textarea element -->
      <Textarea
        :id="textareaId"
        ref="textareaRef"
        :model-value="value"
        :placeholder="placeholder"
        :disabled="disabled || loading"
        :rows="rows"
        :cols="cols"
        :auto-resize="autoResize"
        :class="textareaClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
      />

      <!-- Loading spinner -->
      <div v-if="loading" class="fnx-textarea-loading">
        <div class="fnx-spinner" />
      </div>
    </div>

    <!-- Character counter -->
    <div
      v-if="showCounter && maxLength"
      class="fnx-textarea-counter"
      :class="{ 'fnx-textarea-counter--over-limit': isOverLimit }"
    >
      {{ characterCount }}/{{ maxLength }}
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
import Textarea from 'primevue/textarea'
import type { TextareaProps } from './types/form-types'
import { buildValidationString } from './utils/validation-rules'

// Props
const props = withDefaults(defineProps<TextareaProps>(), {
  size: 'md',
  rows: 3,
  autoResize: false,
  showCounter: false
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string]
  'blur': [event: Event]
  'focus': [event: Event]
  'input': [event: Event]
}>()

// Template refs
const textareaRef = ref<any>()

// Generate unique ID for the textarea
const textareaId = computed(() => `fnx-textarea-${props.name}`)

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
const isOverLimit = computed(() => props.maxLength ? characterCount.value > props.maxLength : false)

const fieldClass = computed(() => [
  props.class,
  {
    'fnx-field--error': !!errorMessage.value,
    'fnx-field--success': meta.valid && meta.touched && !errorMessage.value,
    'fnx-field--disabled': props.disabled,
    'fnx-field--loading': props.loading
  }
])

const textareaClasses = computed(() => [
  'fnx-textarea',
  `fnx-textarea--${props.size}`,
  {
    'fnx-textarea--error': !!errorMessage.value,
    'fnx-textarea--success': meta.valid && meta.touched && !errorMessage.value,
    'fnx-textarea--loading': props.loading,
    'fnx-textarea--auto-resize': props.autoResize
  }
])

// Event handlers
const handleInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  const newValue = target.value
  
  value.value = newValue
  emit('update:modelValue', newValue)
  emit('input', event)
  handleChange(event)
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
  if (textareaRef.value) {
    textareaRef.value.focus()
  }
}

const blur = () => {
  if (textareaRef.value) {
    textareaRef.value.blur()
  }
}

const select = () => {
  if (textareaRef.value) {
    textareaRef.value.select()
  }
}

// Expose methods to parent component
defineExpose({
  focus,
  blur,
  select,
  textareaRef
})
</script>

<style scoped>
.fnx-textarea-wrapper {
  position: relative;
}

.fnx-textarea-loading {
  position: absolute;
  right: var(--fnx-spacing-sm);
  top: var(--fnx-spacing-sm);
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

/* Character counter */
.fnx-textarea-counter {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--fnx-spacing-xs);
  font-size: var(--fnx-font-size-xs);
  color: var(--fnx-text-secondary);
}

.fnx-textarea-counter--over-limit {
  color: var(--fnx-error-500);
  font-weight: var(--fnx-font-weight-medium);
}

/* Size variants */
.fnx-textarea--sm {
  font-size: var(--fnx-font-size-sm);
}

.fnx-textarea--lg {
  font-size: var(--fnx-font-size-lg);
}

/* State variants */
.fnx-textarea--error {
  border-color: var(--fnx-error-500);
}

.fnx-textarea--success {
  border-color: var(--fnx-success-500);
}

.fnx-textarea--loading {
  opacity: 0.7;
}

.fnx-textarea--auto-resize {
  resize: none;
}
</style>
