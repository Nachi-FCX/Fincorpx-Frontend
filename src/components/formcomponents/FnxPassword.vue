<template>
  <div class="fnx-field" :class="fieldClass">
    <!-- Label -->
    <label
      v-if="label"
      :for="inputId"
      class="fnx-field-label"
      :class="{ required }"
      style="font-size: 0.75rem; font-weight: 500; margin-bottom: 0.25rem;"
    >
      {{ label }}
    </label>

    <!-- Password wrapper -->
    <div class="fnx-password-wrapper">
      <!-- Password element -->
      <Password
        :id="inputId"
        ref="passwordRef"
        :model-value="value"
        :placeholder="placeholder"
        :disabled="disabled || loading"
        :toggle-mask="toggleMask"
        :feedback="showStrength"
        :prompt-label="promptLabel"
        :weak-label="weakLabel"
        :medium-label="mediumLabel"
        :strong-label="strongLabel"
        :class="passwordClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
      />

      <!-- Loading spinner -->
      <div v-if="loading" class="fnx-password-loading">
        <div class="fnx-spinner" />
      </div>
    </div>

    <!-- Custom password strength indicator -->
    <div v-if="showStrength && value && !loading" class="fnx-password-strength">
      <div class="fnx-password-strength-bar">
        <div 
          class="fnx-password-strength-fill" 
          :class="`fnx-password-strength-fill--${strengthLevel}`"
          :style="{ width: `${strengthScore}%` }"
        />
      </div>
      <div class="fnx-password-strength-text">
        <span :class="`fnx-password-strength-label--${strengthLevel}`">
          {{ strengthLabel }}
        </span>
        <span class="fnx-password-strength-score">{{ strengthScore }}%</span>
      </div>
      <div v-if="strengthFeedback.length > 0" class="fnx-password-feedback">
        <ul>
          <li v-for="feedback in strengthFeedback" :key="feedback">
            {{ feedback }}
          </li>
        </ul>
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
import Password from 'primevue/password'
import type { PasswordProps } from './types/form-types'
import { buildValidationString, calculatePasswordStrength } from './utils/validation-rules'

// Props
const props = withDefaults(defineProps<PasswordProps>(), {
  size: 'md',
  toggleMask: true,
  showStrength: true,
  feedback: true,
  promptLabel: 'Enter a password',
  weakLabel: 'Weak',
  mediumLabel: 'Medium',
  strongLabel: 'Strong'
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string]
  'blur': [event: Event]
  'focus': [event: Event]
  'input': [event: Event]
}>()

// Template refs
const passwordRef = ref<any>()

// Generate unique ID for the input
const inputId = computed(() => `fnx-password-${props.name}`)

// Build validation rules from props
const validationRules = computed(() => {
  // If legacy rules prop is provided, use it
  if (props.rules) {
    return props.rules
  }
  
  // Otherwise build from props with password validation
  return buildValidationString({
    required: props.required,
    validationType: 'password',
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

// Password strength calculation
const passwordStrength = computed(() => {
  return calculatePasswordStrength(value.value || '')
})

const strengthScore = computed(() => passwordStrength.value.score)
const strengthLevel = computed(() => passwordStrength.value.level)
const strengthFeedback = computed(() => passwordStrength.value.feedback)

const strengthLabel = computed(() => {
  switch (strengthLevel.value) {
    case 'weak':
      return props.weakLabel
    case 'medium':
      return props.mediumLabel
    case 'strong':
      return props.strongLabel
    default:
      return props.weakLabel
  }
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

const passwordClasses = computed(() => [
  'fnx-password',
  `fnx-password--${props.size}`,
  {
    'fnx-password--error': !!errorMessage.value,
    'fnx-password--success': meta.valid && meta.touched && !errorMessage.value,
    'fnx-password--loading': props.loading
  }
])

// Event handlers
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
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
  if (passwordRef.value) {
    passwordRef.value.focus()
  }
}

const blur = () => {
  if (passwordRef.value) {
    passwordRef.value.blur()
  }
}

// Expose methods to parent component
defineExpose({
  focus,
  blur,
  passwordRef
})
</script>

<style scoped lang="scss">
@use './styles/fnx-password.scss';
</style>
