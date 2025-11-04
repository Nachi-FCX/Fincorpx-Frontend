<template>
  <div class="fnx-field" :class="fieldClass">
    <!-- Label -->
    <label
      v-if="label"
      :for="calendarId"
      class="fnx-field-label"
      :class="{ required }"
    >
      {{ label }}
    </label>

    <!-- Calendar wrapper -->
    <div class="fnx-calendar-wrapper">
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
      <div v-if="loading" class="fnx-calendar-loading">
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
const calendarId = computed(() => `fnx-calendar-${props.name}`)

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
    'fnx-field--error': !!errorMessage.value,
    'fnx-field--success': meta.valid && meta.touched && !errorMessage.value,
    'fnx-field--disabled': props.disabled,
    'fnx-field--loading': props.loading
  }
])

const calendarClasses = computed(() => [
  'fnx-calendar',
  `fnx-calendar--${props.size}`,
  {
    'fnx-calendar--error': !!errorMessage.value,
    'fnx-calendar--success': meta.valid && meta.touched && !errorMessage.value,
    'fnx-calendar--loading': props.loading,
    'fnx-calendar--inline': props.inline,
    'fnx-calendar--with-time': props.showTime,
    'fnx-calendar--time-only': props.timeOnly
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
.fnx-calendar-wrapper {
  position: relative;
}

.fnx-calendar-loading {
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
.fnx-calendar--sm {
  font-size: var(--fnx-font-size-sm);
}

.fnx-calendar--lg {
  font-size: var(--fnx-font-size-lg);
}

/* State variants */
.fnx-calendar--error {
  border-color: var(--fnx-error-500);
}

.fnx-calendar--success {
  border-color: var(--fnx-success-500);
}

.fnx-calendar--loading {
  opacity: 0.7;
}

/* Inline calendar styling */
.fnx-calendar--inline {
  display: block;
  width: 100%;
}

/* Time picker styling */
.fnx-calendar--with-time :deep(.p-calendar-time-picker) {
  border-top: 1px solid var(--fnx-border-normal);
  padding-top: var(--fnx-spacing-sm);
}

.fnx-calendar--time-only :deep(.p-datepicker-calendar) {
  display: none;
}

/* Custom calendar styling */
.fnx-calendar :deep(.p-inputtext) {
  border-radius: var(--fnx-border-radius-md);
  transition: all var(--fnx-transition-duration) var(--fnx-transition-timing);
}

.fnx-calendar :deep(.p-inputtext:hover) {
  border-color: var(--fnx-primary-400);
}

.fnx-calendar :deep(.p-inputtext:focus) {
  outline: 2px solid var(--fnx-primary-200);
  outline-offset: 2px;
  border-color: var(--fnx-primary-500);
}

.fnx-calendar--error :deep(.p-inputtext) {
  border-color: var(--fnx-error-500);
}

.fnx-calendar--success :deep(.p-inputtext) {
  border-color: var(--fnx-success-500);
}

/* Calendar icon styling */
.fnx-calendar :deep(.p-datepicker-trigger) {
  background: transparent;
  border: none;
  color: var(--fnx-text-secondary);
  transition: color var(--fnx-transition-duration) var(--fnx-transition-timing);
}

.fnx-calendar :deep(.p-datepicker-trigger:hover) {
  color: var(--fnx-primary-500);
}

/* Calendar panel styling */
.fnx-calendar :deep(.p-datepicker) {
  border-radius: var(--fnx-border-radius-lg);
  box-shadow: var(--fnx-shadow-lg);
  border: 1px solid var(--fnx-border-normal);
}

.fnx-calendar :deep(.p-datepicker-header) {
  background: var(--fnx-surface);
  border-bottom: 1px solid var(--fnx-border-light);
  border-radius: var(--fnx-border-radius-lg) var(--fnx-border-radius-lg) 0 0;
}

.fnx-calendar :deep(.p-datepicker-calendar td > span) {
  border-radius: var(--fnx-border-radius-sm);
  transition: all var(--fnx-transition-duration) var(--fnx-transition-timing);
}

.fnx-calendar :deep(.p-datepicker-calendar td > span:hover) {
  background: var(--fnx-primary-100);
  color: var(--fnx-primary-700);
}

.fnx-calendar :deep(.p-datepicker-calendar td > span.p-highlight) {
  background: var(--fnx-primary-500);
  color: var(--fnx-text-inverse);
}
</style>
