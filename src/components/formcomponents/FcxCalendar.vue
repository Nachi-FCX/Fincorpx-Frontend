<template>
  <div class="fcx-field" :class="fieldClass">
    <!-- Label -->
    <label
      v-if="label"
      :for="calendarId"
      class="fcx-field-label"
      :class="{ required }"
    >
      {{ label }}
    </label>

    <!-- Calendar wrapper -->
    <div class="fcx-calendar-wrapper">
      <!-- Calendar element -->
      <DatePicker
        :id="calendarId"
        ref="calendarRef"
        :model-value="value"
        :placeholder="placeholder"
        :disabled="disabled || loading"
        :selection-mode="selectionMode"
        :date-format="dateFormat"
        :show-time="showTime"
        :time-only="timeOnly"
        :hour-format="hourFormat"
        :show-seconds="showSeconds"
        :show-milliseconds="showMilliseconds"
        :min-date="minDate"
        :max-date="maxDate"
        :disabled-dates="disabledDates"
        :disabled-days="disabledDays"
        :show-on-focus="showOnFocus"
        :show-week="showWeek"
        :show-other-months="showOtherMonths"
        :select-other-months="selectOtherMonths"
        :show-icon="showIcon"
        :icon="icon"
        :number-of-months="numberOfMonths"
        :view="view"
        :touch-u-i="touchUI"
        :month-navigator="monthNavigator"
        :year-navigator="yearNavigator"
        :year-range="yearRange"
        :inline="inline"
        :class="calendarClasses"
        @date-select="handleDateSelect"
        @show="handleShow"
        @hide="handleHide"
        @month-change="handleMonthChange"
        @year-change="handleYearChange"
        @blur="handleBlur"
        @focus="handleFocus"
      />

      <!-- Loading spinner -->
      <div v-if="loading" class="fcx-calendar-loading">
        <div class="fcx-spinner" />
      </div>
    </div>

    <!-- Error message -->
    <div v-if="errorMessage" class="fcx-field-error">
      <svg class="fcx-error-icon" viewBox="0 0 20 20" fill="currentColor">
        <path
          fill-rule="evenodd"
          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
          clip-rule="evenodd"
        />
      </svg>
      {{ errorMessage }}
    </div>

    <!-- Help text -->
    <div v-if="help && !errorMessage" class="fcx-field-help">
      {{ help }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useField } from 'vee-validate'
import DatePicker from 'primevue/datepicker'
import type { CalendarProps } from './types/form-types'
import { buildValidationString } from './utils/validation-rules'

// Props
const props = withDefaults(defineProps<CalendarProps>(), {
  size: 'md',
  selectionMode: 'single',
  dateFormat: 'mm/dd/yy',
  hourFormat: '24',
  showOnFocus: true,
  showOtherMonths: true,
  selectOtherMonths: false,
  showIcon: true,
  icon: 'pi pi-calendar',
  numberOfMonths: 1,
  view: 'date',
  touchUI: false,
  monthNavigator: false,
  yearNavigator: false,
  yearRange: '1900:2030',
  inline: false,
  showTime: false,
  timeOnly: false,
  showSeconds: false,
  showMilliseconds: false,
  showWeek: false
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: Date | Date[] | null]
  'date-select': [event: { originalEvent: Event; value: Date | Date[] }]
  'show': []
  'hide': []
  'month-change': [event: { month: number; year: number }]
  'year-change': [event: { month: number; year: number }]
  'blur': [event: Event]
  'focus': [event: Event]
}>()

// Template refs
const calendarRef = ref<any>()

// Generate unique ID for the calendar
const calendarId = computed(() => `fcx-calendar-${props.name}`)

// Build validation rules from props
const validationRules = computed(() => {
  // If legacy rules prop is provided, use it
  if (props.rules) {
    return props.rules
  }
  
  // Build from props
  return buildValidationString({
    required: props.required,
    validationType: 'date',
    minDate: props.minDate,
    maxDate: props.maxDate
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
    'fcx-field--error': !!errorMessage.value,
    'fcx-field--success': meta.valid && meta.touched && !errorMessage.value,
    'fcx-field--disabled': props.disabled,
    'fcx-field--loading': props.loading
  }
])

const calendarClasses = computed(() => [
  'fcx-calendar',
  `fcx-calendar--${props.size}`,
  {
    'fcx-calendar--error': !!errorMessage.value,
    'fcx-calendar--success': meta.valid && meta.touched && !errorMessage.value,
    'fcx-calendar--loading': props.loading,
    'fcx-calendar--inline': props.inline,
    'fcx-calendar--with-time': props.showTime,
    'fcx-calendar--time-only': props.timeOnly
  }
])

// Event handlers
const handleDateSelect = (event: any) => {
  value.value = event.value
  emit('update:modelValue', event.value)
  emit('date-select', event)
  veeHandleChange(event.originalEvent || event)
}

const handleShow = () => {
  emit('show')
}

const handleHide = () => {
  emit('hide')
}

const handleMonthChange = (event: any) => {
  emit('month-change', event)
}

const handleYearChange = (event: any) => {
  emit('year-change', event)
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
  if (calendarRef.value) {
    calendarRef.value.focus()
  }
}

const blur = () => {
  if (calendarRef.value) {
    calendarRef.value.blur()
  }
}

const show = () => {
  if (calendarRef.value) {
    calendarRef.value.show()
  }
}

const hide = () => {
  if (calendarRef.value) {
    calendarRef.value.hide()
  }
}

// Expose methods to parent component
defineExpose({
  focus,
  blur,
  show,
  hide,
  calendarRef
})
</script>

<style scoped>
fcx-calendar-wrapper {
  position: relative;
}

fcx-calendar-loading {
  position: absolute;
  right: var(--fcx-spacing-sm);
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

fcx-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--fcx-border-light);
  border-top: 2px solid var(--fcx-primary-500);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Size variants */
fcx-calendar--sm {
  font-size: var(--fcx-font-size-sm);
}

fcx-calendar--lg {
  font-size: var(--fcx-font-size-lg);
}

/* State variants */
fcx-calendar--error {
  border-color: var(--fcx-error-500);
}

fcx-calendar--success {
  border-color: var(--fcx-success-500);
}

fcx-calendar--loading {
  opacity: 0.7;
}

/* Inline calendar styling */
fcx-calendar--inline {
  display: block;
  width: 100%;
}

/* Time picker styling */
fcx-calendar--with-time :deep(.p-calendar-time-picker) {
  border-top: 1px solid var(--fcx-border-normal);
  padding-top: var(--fcx-spacing-sm);
}

fcx-calendar--time-only :deep(.p-datepicker-calendar) {
  display: none;
}

/* Custom calendar styling */
fcx-calendar :deep(.p-inputtext) {
  border-radius: var(--fcx-border-radius-md);
  transition: all var(--fcx-transition-duration) var(--fcx-transition-timing);
}

fcx-calendar :deep(.p-inputtext:hover) {
  border-color: var(--fcx-primary-400);
}

fcx-calendar :deep(.p-inputtext:focus) {
  outline: 2px solid var(--fcx-primary-200);
  outline-offset: 2px;
  border-color: var(--fcx-primary-500);
}

fcx-calendar--error :deep(.p-inputtext) {
  border-color: var(--fcx-error-500);
}

fcx-calendar--success :deep(.p-inputtext) {
  border-color: var(--fcx-success-500);
}

/* Calendar icon styling */
fcx-calendar :deep(.p-datepicker-trigger) {
  background: transparent;
  border: none;
  color: var(--fcx-text-secondary);
  transition: color var(--fcx-transition-duration) var(--fcx-transition-timing);
}

fcx-calendar :deep(.p-datepicker-trigger:hover) {
  color: var(--fcx-primary-500);
}

/* Calendar panel styling */
fcx-calendar :deep(.p-datepicker) {
  border-radius: var(--fcx-border-radius-lg);
  box-shadow: var(--fcx-shadow-lg);
  border: 1px solid var(--fcx-border-normal);
}

fcx-calendar :deep(.p-datepicker-header) {
  background: var(--fcx-surface);
  border-bottom: 1px solid var(--fcx-border-light);
  border-radius: var(--fcx-border-radius-lg) var(--fcx-border-radius-lg) 0 0;
}

fcx-calendar :deep(.p-datepicker-calendar td > span) {
  border-radius: var(--fcx-border-radius-sm);
  transition: all var(--fcx-transition-duration) var(--fcx-transition-timing);
}

fcx-calendar :deep(.p-datepicker-calendar td > span:hover) {
  background: var(--fcx-primary-100);
  color: var(--fcx-primary-700);
}

fcx-calendar :deep(.p-datepicker-calendar td > span.p-highlight) {
  background: var(--fcx-primary-500);
  color: var(--fcx-text-inverse);
}
</style>
