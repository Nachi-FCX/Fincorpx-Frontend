<template>
  <div class="form-demo">
    <div class="demo-container">
      <h1>FNX Form Components Demo</h1>
      
      <!-- Theme Switcher -->
      <div class="theme-switcher">
        <h2>Theme Switcher</h2>
        <div class="theme-buttons">
          <button 
            @click="setTheme('light')" 
            :class="{ active: currentTheme === 'light' }"
            class="theme-btn"
          >
            Light
          </button>
          <button 
            @click="setTheme('dark')" 
            :class="{ active: currentTheme === 'dark' }"
            class="theme-btn"
          >
            Dark
          </button>
          <button 
            @click="setTheme('system')" 
            :class="{ active: currentTheme === 'system' }"
            class="theme-btn"
          >
            System
          </button>
        </div>
        <p class="theme-info">
          Current theme: <strong>{{ currentTheme }}</strong> 
          (Resolved: <strong>{{ resolvedTheme }}</strong>)
        </p>
      </div>

      <!-- Form Demo -->
      <div class="form-section">
        <h2>Comprehensive Form Components Test</h2>
        
        <!-- VeeValidate Form -->
        <Form @submit="handleSubmit" class="demo-form" v-slot="{ errors, meta }">
          <!-- Text Input Components -->
          <div class="form-group">
            <h3>Text Input Components</h3>
            
            <div class="form-row">
              <FnxInputtext
                name="firstName"
                label="First Name"
                placeholder="Enter your first name"
                :required="true"
                :min-length="2"
                :max-length="50"
                v-model="formData.firstName"
                help="Required field with 2-50 characters"
                size="md"
              />
              
              <FnxInputtext
                name="email"
                label="Email Address"
                type="email"
                placeholder="Enter your email"
                :required="true"
                validation-type="email"
                v-model="formData.email"
                clearable
                size="md"
              />
            </div>

            <div class="form-row">
              <FnxInputtext
                name="phone"
                label="Phone Number"
                type="tel"
                placeholder="Enter your phone number"
                validation-type="phone"
                v-model="formData.phone"
                size="sm"
              />
              
              <FnxInputtext
                name="website"
                label="Website"
                type="url"
                placeholder="https://example.com"
                validation-type="url"
                v-model="formData.website"
                :disabled="formDisabled"
                size="lg"
              />
            </div>
          </div>

          <!-- Number and Password Components -->
          <div class="form-group">
            <h3>Number & Password Components</h3>
            
            <div class="form-row">
              <FnxInputNumber
                name="age"
                label="Age"
                placeholder="Enter your age"
                :required="true"
                :min="18"
                :max="100"
                v-model="formData.age"
                help="Must be between 18 and 100"
              />
              
              <FnxInputNumber
                name="salary"
                label="Salary"
                placeholder="Enter your salary"
                :min="0"
                :fraction-digits="2"
                prefix="$"
                :show-buttons="true"
                v-model="formData.salary"
                size="lg"
              />
            </div>

            <div class="form-row">
              <FnxPassword
                name="password"
                label="Password"
                placeholder="Enter your password"
                :required="true"
                :min-length="8"
                :show-strength="true"
                v-model="formData.password"
                :loading="passwordLoading"
              />
              
              <FnxPassword
                name="confirmPassword"
                label="Confirm Password"
                placeholder="Confirm your password"
                :required="true"
                :show-strength="false"
                v-model="formData.confirmPassword"
              />
            </div>
          </div>

          <!-- Textarea Components -->
          <div class="form-group">
            <h3>Textarea Components</h3>
            
            <div class="form-row">
              <FnxTextarea
                name="description"
                label="Description"
                placeholder="Enter a description"
                :required="true"
                :min-length="10"
                :max-length="500"
                :rows="4"
                :show-counter="true"
                :auto-resize="true"
                v-model="formData.description"
              />
              
              <FnxTextarea
                name="comments"
                label="Comments"
                placeholder="Enter your comments"
                :rows="3"
                :max-length="200"
                :show-counter="true"
                v-model="formData.comments"
                help="Optional comments field"
              />
            </div>
          </div>

          <!-- Selection Components -->
          <div class="form-group">
            <h3>Selection Components</h3>
            
            <div class="form-row">
              <FnxDropdown
                name="country"
                label="Country"
                placeholder="Select your country"
                :options="countries"
                option-label="name"
                option-value="code"
                :required="true"
                v-model="formData.country"
                filter
                show-clear
              />
              
              <FnxMultiSelect
                name="skills"
                label="Skills"
                placeholder="Select your skills"
                :options="skills"
                v-model="formData.skills"
                filter
                :max-selected-labels="3"
                selected-items-label="{0} skills selected"
                display="chip"
              />
            </div>

            <div class="form-row">
              <FnxAutoComplete
                name="city"
                label="City"
                placeholder="Type to search cities"
                :suggestions="filteredCities"
                v-model="formData.city"
                @complete="searchCities"
                :min-length="2"
                :delay="300"
              />
              
              <FnxCalendar
                name="birthDate"
                label="Birth Date"
                placeholder="Select your birth date"
                :required="true"
                :max-date="new Date()"
                :min-date="new Date('1900-01-01')"
                v-model="formData.birthDate"
                :show-icon="true"
                date-format="mm/dd/yy"
              />
            </div>
          </div>

          <!-- Boolean Components -->
          <div class="form-group">
            <h3>Boolean & Choice Components</h3>
            
            <div class="form-row">
              <div class="checkbox-group">
                <h4>Interests (Checkboxes)</h4>
                <FnxCheckbox
                  name="interests"
                  label="Technology"
                  value="technology"
                  :binary="false"
                  v-model="formData.interests"
                />
                <FnxCheckbox
                  name="interests"
                  label="Sports"
                  value="sports"
                  :binary="false"
                  v-model="formData.interests"
                />
                <FnxCheckbox
                  name="interests"
                  label="Music"
                  value="music"
                  :binary="false"
                  v-model="formData.interests"
                />
              </div>
              
              <div class="radio-group">
                <h4>Experience Level (Radio Buttons)</h4>
                <FnxRadioButton
                  name="experience"
                  label="Beginner"
                  value="beginner"
                  v-model="formData.experience"
                />
                <FnxRadioButton
                  name="experience"
                  label="Intermediate"
                  value="intermediate"
                  v-model="formData.experience"
                />
                <FnxRadioButton
                  name="experience"
                  label="Advanced"
                  value="advanced"
                  v-model="formData.experience"
                />
              </div>
            </div>

            <div class="form-row">
              <FnxToggleButton
                name="newsletter"
                label="Newsletter Subscription"
                v-model="formData.newsletter"
                on-label="Subscribed"
                off-label="Not Subscribed"
                on-icon="pi pi-check"
                off-icon="pi pi-times"
              />
              
              <FnxToggleButton
                name="notifications"
                label="Push Notifications"
                v-model="formData.notifications"
                on-label="Enabled"
                off-label="Disabled"
                :loading="isToggleLoading"
              />
            </div>
          </div>

          <!-- Advanced Calendar -->
          <div class="form-group">
            <h3>Advanced Calendar Components</h3>
            
            <div class="form-row">
              <FnxCalendar
                name="meetingDate"
                label="Meeting Date & Time"
                placeholder="Select meeting date and time"
                :show-time="true"
                :show-seconds="true"
                hour-format="24"
                v-model="formData.meetingDate"
                :min-date="new Date()"
              />
              
              <FnxCalendar
                name="vacationDates"
                label="Vacation Period"
                placeholder="Select vacation dates"
                selection-mode="range"
                :number-of-months="2"
                v-model="formData.vacationDates"
                :disabled-days="[0, 6]"
              />
            </div>
          </div>

          <!-- Form Actions -->
          <div class="form-actions">
            <button type="submit" class="submit-btn">
              Submit Form
            </button>
            <button type="button" @click="resetForm" class="reset-btn">
              Reset Form
            </button>
            <button type="button" @click="toggleDisabled" class="toggle-btn">
              {{ formDisabled ? 'Enable' : 'Disable' }} Form
            </button>
            <button type="button" @click="toggleLoading" class="toggle-btn">
              {{ passwordLoading ? 'Stop' : 'Start' }} Loading
            </button>
            <button type="button" @click="validateForm" class="validate-btn">
              Validate All
            </button>
          </div>

          <!-- Validation Summary -->
          <div v-if="Object.keys(errors).length > 0" class="validation-summary">
            <h3>Validation Errors</h3>
            <ul>
              <li v-for="(error, field) in errors" :key="field">
                <strong>{{ field }}:</strong> {{ error }}
              </li>
            </ul>
          </div>

          <!-- Form Meta Information -->
          <div class="form-meta">
            <h3>Form Status</h3>
            <div class="meta-grid">
              <div class="meta-item">
                <span class="meta-label">Valid:</span>
                <span class="meta-value" :class="{ 'meta-value--success': meta.valid, 'meta-value--error': !meta.valid }">
                  {{ meta.valid ? 'Yes' : 'No' }}
                </span>
              </div>
              <div class="meta-item">
                <span class="meta-label">Touched:</span>
                <span class="meta-value">{{ meta.touched ? 'Yes' : 'No' }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">Dirty:</span>
                <span class="meta-value">{{ meta.dirty ? 'Yes' : 'No' }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">Pending:</span>
                <span class="meta-value">{{ meta.pending ? 'Yes' : 'No' }}</span>
              </div>
            </div>
          </div>

          <!-- Form Data Display -->
          <div class="form-data">
            <h3>Form Data (Live Preview)</h3>
            <pre>{{ JSON.stringify(formData, null, 2) }}</pre>
          </div>
        </Form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Form } from 'vee-validate'
import { useTheme } from '../../composables/useTheme'

// Theme management
const { currentTheme, resolvedTheme, setTheme } = useTheme()

// Form state
const formDisabled = ref(false)
const passwordLoading = ref(false)
const isToggleLoading = ref(false)

// Form data
const formData = reactive({
  // Text inputs
  firstName: '',
  email: '',
  phone: '',
  website: '',
  
  // Numbers and passwords
  age: null as number | null,
  salary: null as number | null,
  password: '',
  confirmPassword: '',
  
  // Textarea and masks
  description: '',
  comments: '',
  ssn: '',
  phoneFormatted: '',
  dateFormatted: '',
  
  // Selections
  country: '',
  skills: [] as string[],
  city: '',
  birthDate: null as Date | null,
  
  // Boolean choices
  interests: [] as string[],
  experience: '',
  newsletter: false,
  notifications: false,
  
  // Advanced calendar
  meetingDate: null as Date | null,
  vacationDates: null as Date[] | null
})

// Options data
const countries = [
  { name: 'United States', code: 'US' },
  { name: 'Canada', code: 'CA' },
  { name: 'United Kingdom', code: 'UK' },
  { name: 'Germany', code: 'DE' },
  { name: 'France', code: 'FR' },
  { name: 'Japan', code: 'JP' },
  { name: 'Australia', code: 'AU' },
  { name: 'India', code: 'IN' }
]

const skills = [
  'JavaScript', 'TypeScript', 'Vue.js', 'React', 'Angular',
  'Node.js', 'Python', 'Java', 'C#', 'PHP', 'Go', 'Rust'
]

const cities = [
  'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
  'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose',
  'Austin', 'Jacksonville', 'Fort Worth', 'Columbus', 'Charlotte'
]

const filteredCities = ref<string[]>([])

// Methods
const searchCities = (event: { query: string }) => {
  filteredCities.value = cities.filter(city => 
    city.toLowerCase().includes(event.query.toLowerCase())
  )
}

const handleSubmit = (values: any) => {
  console.log('Form submitted:', values)
  console.log('Form data:', formData)
  
  // Validate passwords match
  if (formData.password !== formData.confirmPassword) {
    alert('Passwords do not match!')
    return
  }
  
  alert('Form submitted successfully! Check console for data.')
}

const resetForm = () => {
  Object.keys(formData).forEach(key => {
    const value = formData[key as keyof typeof formData]
    if (Array.isArray(value)) {
      (formData[key as keyof typeof formData] as any[]) = []
    } else if (typeof value === 'boolean') {
      (formData[key as keyof typeof formData] as any) = false
    } else if (typeof value === 'number') {
      (formData[key as keyof typeof formData] as any) = null
    } else {
      (formData[key as keyof typeof formData] as any) = ''
    }
  })
}

const toggleDisabled = () => {
  formDisabled.value = !formDisabled.value
}

const toggleLoading = () => {
  passwordLoading.value = !passwordLoading.value
  isToggleLoading.value = !isToggleLoading.value
  
  if (passwordLoading.value) {
    setTimeout(() => {
      passwordLoading.value = false
      isToggleLoading.value = false
    }, 3000)
  }
}

const validateForm = () => {
  // This will trigger validation on all fields
  const form = document.querySelector('form')
  if (form) {
    const submitEvent = new Event('submit', { bubbles: true, cancelable: true })
    form.dispatchEvent(submitEvent)
  }
}
</script>

<style scoped>
.form-demo {
  min-height: 100vh;
  background: var(--fnx-background);
  color: var(--fnx-text-primary);
  padding: var(--fnx-spacing-md);
}

.demo-container {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

@media (min-width: 768px) {
  .form-demo {
    padding: var(--fnx-spacing-xl);
  }
}

h1 {
  font-size: 2.5rem;
  font-weight: var(--fnx-font-weight-semibold);
  margin-bottom: var(--fnx-spacing-xl);
  text-align: center;
  color: var(--fnx-primary-600);
}

h2 {
  font-size: 1.5rem;
  font-weight: var(--fnx-font-weight-medium);
  margin-bottom: var(--fnx-spacing-lg);
  color: var(--fnx-text-primary);
}

h3 {
  font-size: 1.25rem;
  font-weight: var(--fnx-font-weight-medium);
  margin-bottom: var(--fnx-spacing-md);
  color: var(--fnx-text-primary);
  border-bottom: 2px solid var(--fnx-primary-200);
  padding-bottom: var(--fnx-spacing-sm);
}

h4 {
  font-size: 1rem;
  font-weight: var(--fnx-font-weight-medium);
  margin-bottom: var(--fnx-spacing-sm);
  color: var(--fnx-text-primary);
}

.theme-switcher {
  background: var(--fnx-surface);
  border: 1px solid var(--fnx-border-normal);
  border-radius: var(--fnx-border-radius-lg);
  padding: var(--fnx-spacing-xl);
  margin-bottom: var(--fnx-spacing-xl);
}

.theme-buttons {
  display: flex;
  gap: var(--fnx-spacing-sm);
  margin-bottom: var(--fnx-spacing-md);
}

.theme-btn {
  padding: var(--fnx-spacing-sm) var(--fnx-spacing-lg);
  border: 1px solid var(--fnx-border-normal);
  border-radius: var(--fnx-border-radius-md);
  background: var(--fnx-surface);
  color: var(--fnx-text-primary);
  cursor: pointer;
  transition: all var(--fnx-transition-duration) var(--fnx-transition-timing);
}

.theme-btn:hover {
  background: var(--fnx-surface-hover);
  border-color: var(--fnx-border-strong);
}

.theme-btn.active {
  background: var(--fnx-primary-500);
  color: var(--fnx-text-inverse);
  border-color: var(--fnx-primary-500);
}

.theme-info {
  color: var(--fnx-text-secondary);
  font-size: var(--fnx-font-size-sm);
}

.form-section {
  background: var(--fnx-surface);
  border: 1px solid var(--fnx-border-normal);
  border-radius: var(--fnx-border-radius-lg);
  padding: var(--fnx-spacing-xl);
}

.demo-form {
  display: flex;
  flex-direction: column;
  gap: var(--fnx-spacing-xl);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--fnx-spacing-lg);
  padding: var(--fnx-spacing-lg);
  background: var(--fnx-surface-active);
  border-radius: var(--fnx-border-radius-md);
  border: 1px solid var(--fnx-border-light);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--fnx-spacing-lg);
}

.checkbox-group,
.radio-group {
  display: flex;
  flex-direction: column;
  gap: var(--fnx-spacing-sm);
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

.form-actions {
  display: flex;
  gap: var(--fnx-spacing-md);
  flex-wrap: wrap;
  padding: var(--fnx-spacing-lg);
  background: var(--fnx-surface-active);
  border-radius: var(--fnx-border-radius-md);
  border: 1px solid var(--fnx-border-light);
}

.submit-btn,
.reset-btn,
.toggle-btn,
.validate-btn {
  padding: var(--fnx-spacing-md) var(--fnx-spacing-lg);
  border-radius: var(--fnx-border-radius-md);
  font-weight: var(--fnx-font-weight-medium);
  cursor: pointer;
  transition: all var(--fnx-transition-duration) var(--fnx-transition-timing);
  border: 1px solid;
}

.submit-btn {
  background: var(--fnx-primary-500);
  color: var(--fnx-text-inverse);
  border-color: var(--fnx-primary-500);
}

.submit-btn:hover:not(:disabled) {
  background: var(--fnx-primary-600);
  border-color: var(--fnx-primary-600);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.reset-btn {
  background: var(--fnx-surface);
  color: var(--fnx-text-primary);
  border-color: var(--fnx-border-normal);
}

.reset-btn:hover {
  background: var(--fnx-surface-hover);
  border-color: var(--fnx-border-strong);
}

.toggle-btn {
  background: var(--fnx-surface);
  color: var(--fnx-text-secondary);
  border-color: var(--fnx-border-normal);
}

.toggle-btn:hover {
  background: var(--fnx-surface-hover);
  color: var(--fnx-text-primary);
  border-color: var(--fnx-border-strong);
}

.validate-btn {
  background: var(--fnx-warning-500);
  color: var(--fnx-text-inverse);
  border-color: var(--fnx-warning-500);
}

.validate-btn:hover {
  background: var(--fnx-warning-600);
  border-color: var(--fnx-warning-600);
}

.validation-summary {
  background: var(--fnx-error-50);
  border: 1px solid var(--fnx-error-200);
  border-radius: var(--fnx-border-radius-md);
  padding: var(--fnx-spacing-lg);
}

.validation-summary h3 {
  color: var(--fnx-error-700);
  margin-bottom: var(--fnx-spacing-md);
}

.validation-summary ul {
  margin: 0;
  padding-left: var(--fnx-spacing-md);
}

.validation-summary li {
  color: var(--fnx-error-600);
  margin-bottom: var(--fnx-spacing-xs);
}

.form-meta {
  background: var(--fnx-surface-active);
  border: 1px solid var(--fnx-border-light);
  border-radius: var(--fnx-border-radius-md);
  padding: var(--fnx-spacing-lg);
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--fnx-spacing-md);
}

.meta-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--fnx-spacing-sm);
  background: var(--fnx-surface);
  border-radius: var(--fnx-border-radius-sm);
  border: 1px solid var(--fnx-border-light);
}

.meta-label {
  font-weight: var(--fnx-font-weight-medium);
  color: var(--fnx-text-secondary);
}

.meta-value {
  font-weight: var(--fnx-font-weight-semibold);
  color: var(--fnx-text-primary);
}

.meta-value--success {
  color: var(--fnx-success-600);
}

.meta-value--error {
  color: var(--fnx-error-600);
}

.form-data {
  background: var(--fnx-surface-active);
  border: 1px solid var(--fnx-border-light);
  border-radius: var(--fnx-border-radius-md);
  padding: var(--fnx-spacing-lg);
}

.form-data pre {
  font-family: 'Courier New', monospace;
  font-size: var(--fnx-font-size-sm);
  color: var(--fnx-text-secondary);
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  max-height: 400px;
  overflow-y: auto;
}
</style>
