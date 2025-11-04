<template>
  <aside 
    class="sidebar" 
    :class="{ 
      collapsed: isCollapsed,
      visible: isVisible 
    }"
    :style="sidebarStyles"
  >
    <!-- Sidebar Header - ChatGPT style with logo -->
    <!-- Debug info: Screen: {{ screenWidth }}px, Sidebar: {{ dynamicSidebarWidth }}px, Collapsed: {{ dynamicCollapsedWidth }}px -->
    <div class="sidebar-header">
      
       <img 
       v-if="isCollapsed"
       

          src="@/assets/img/mainasset/fnxlogo.png" 
        alt="FNX" 
        class="company-logo" 
      />
      <img v-else
        src="@/assets/img/mainasset/fnxname.svg" 
        alt="FNX" 
        class="company-logo-name" 
      />
      <!-- <span class="company-name" v-show="!isCollapsed">FINCORP</span> -->
    </div>

    <!-- Top Menu Section -->
    <div class="sidebar-top">
      <nav class="sidebar-nav">
        <SidebarMenuItem
          v-for="item in topMenuItems"
          :key="item.id"
          :item="item"
          :is-collapsed="isCollapsed"
          @click="handleMenuClick"
        />
      </nav>
    </div>

    <!-- Bottom Menu Section -->
    <div class="sidebar-bottom">
      <!-- Separator Line -->
      <div class="sidebar-separator"></div>
      
      <!-- Language Switcher -->
      <SidebarLanguageSwitcher :is-collapsed="isCollapsed" />
      
      <!-- Bottom Menu Items (Support, Settings) -->
      <!-- <div class="bottom-menu-items">
        <SidebarMenuItem
          v-for="item in bottomMenuItems"
          :key="item.id"
          :item="item"
          :is-collapsed="isCollapsed"
          @click="handleMenuClick"
        />
      </div> -->

      <!-- User Profile -->
      <SidebarProfile
        :user="userProfile"
        :is-collapsed="isCollapsed"
        @click="handleProfileClick"
      />
    </div>

    <!-- Toggle Button -->
    <button 
      class="sidebar-toggle"
      @click="toggleSidebar"
      :title="isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
    >
      <svg 
        class="toggle-icon" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path 
          stroke-linecap="round" 
          stroke-linejoin="round" 
          stroke-width="2" 
          d="M15 19l-7-7 7-7"
        />
      </svg>
    </button>
  </aside>

  <!-- Mobile Backdrop -->
  <div 
    v-if="isMobile && isVisible" 
    class="sidebar-backdrop"
    @click="closeSidebar"
  ></div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useSidebar } from './composables/useSidebar'
import { useTheme } from '@/composables/useTheme'
import { useI18n } from '@/composables/useI18n'
import SidebarMenuItem from './SidebarMenuItem.vue'
import SidebarProfile from './SidebarProfile.vue'
import SidebarLanguageSwitcher from './SidebarLanguageSwitcher.vue'
import type { MenuItem, UserProfile } from './types/sidebar-types'

// CSS custom properties for dynamic values using composable
const sidebarStyles = computed(() => ({
  '--dynamic-sidebar-width': `${dynamicSidebarWidth.value}px`,
  '--dynamic-collapsed-width': `${dynamicCollapsedWidth.value}px`
}))

// Props
interface Props {
  isMobileOpen?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isMobileOpen: false
})

// Emits
const emit = defineEmits<{
  'close': []
  'sidebar-collapsed': [value: boolean]
}>()

// Composables
const {
  isCollapsed,
  topMenuItems,
  bottomMenuItems,
  userProfile,
  toggleSidebar,
  navigateToRoute,
  setActiveMenuItem,
  dynamicSidebarWidth,
  dynamicCollapsedWidth,
  screenWidth
} = useSidebar()

const { resolvedTheme, setTheme } = useTheme()
const { isCurrentRTL } = useI18n()

// Local state
const isMobile = ref(window.innerWidth < 600)

// Theme toggle function
const toggleTheme = () => {
  setTheme(resolvedTheme.value === 'dark' ? 'light' : 'dark')
}

// Computed for sidebar visibility
const isVisible = computed(() => {
  if (isMobile.value) {
    return props.isMobileOpen
  }
  return true // Always visible on desktop
})

// Methods
const handleMenuClick = (item: MenuItem, event: MouseEvent): void => {
  // If sidebar is collapsed, expand it first
  if (isCollapsed.value) {
    toggleSidebar()
  }
  
  setActiveMenuItem(item.id)
  
  if (item.route) {
    navigateToRoute(item.route)
  }
  
  // Close sidebar on mobile after navigation
  if (isMobile.value) {
    closeSidebar()
  }
}

const handleProfileClick = (user: UserProfile, event: MouseEvent): void => {
  // Don't automatically navigate to profile route
  // Let the SidebarProfile component handle dropdown toggle
  // Navigation will happen through the dropdown menu items
  
  // Close sidebar on mobile after profile click
  if (isMobile.value) {
    closeSidebar()
  }
  
  console.log('Profile clicked:', user)
}

const closeSidebar = (): void => {
  if (isMobile.value) {
    emit('close')
  }
}

// Handle window resize
const handleResize = () => {
  isMobile.value = window.innerWidth < 600
}

// Keyboard navigation
const handleKeydown = (event: KeyboardEvent): void => {
  if (event.key === 'Escape' && isMobile.value && isVisible.value) {
    closeSidebar()
  }
}

// Watch isCollapsed changes and emit to parent
watch(() => isCollapsed.value, (newValue) => {
  emit('sidebar-collapsed', newValue)
}, { immediate: true })

// Expose methods for parent component
defineExpose({
  toggleSidebar,
  closeSidebar
})

// Lifecycle
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('resize', handleResize)
})
</script>

<style lang="scss" scoped>
// Theme variables
:root {
  // Default to light theme
  --sidebar-bg: #ffffff;
  --sidebar-border: #e5e7eb;
  --sidebar-border-right: #e5e7eb;
  --sidebar-text: #374151;
  --sidebar-hover: #f3f4f6;
  --sidebar-shadow: rgba(0, 0, 0, 0.1);
}

:root[data-theme="light"] {
  // Light theme
  --sidebar-bg: #ffffff;
  --sidebar-border: #e5e7eb;
  --sidebar-border-right: #e5e7eb;
  --sidebar-text: #374151;
  --sidebar-hover: #f3f4f6;
  --sidebar-shadow: rgba(0, 0, 0, 0.1);
}

:root[data-theme="dark"] {
  // Dark theme - Exact ChatGPT colors
  --sidebar-bg: #171717;
  --sidebar-border: #2d2d2d;
  --sidebar-border-right: #2d2d2d;
  --sidebar-text: #ececec;
  --sidebar-hover: #2d2d2d;
  --sidebar-shadow: rgba(0, 0, 0, 0.5);
}

// Main Sidebar Container - ChatGPT style (full height) with dynamic width
.sidebar {
  width: var(--dynamic-sidebar-width, 250px);
  background: var(--sidebar-bg) !important;
  box-shadow: 0 2px 8px var(--sidebar-shadow) !important;
  transition: width 0.3s ease, transform 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100vh;
  flex-shrink: 0;

  &.collapsed {
    width: var(--dynamic-collapsed-width, 60px);

    .company-name {
      opacity: 0;
      width: 0;
    }

    :deep(.menu-text) {
      opacity: 0;
      width: 0;
    }

    :deep(.profile-info) {
      opacity: 0;
      width: 0;
    }
  }

  // Mobile styles - Only apply fixed positioning and overlay behavior for small screens
  @media (max-width: 767px) {
    position: fixed !important;
    top: 0;
    left: 0;
    z-index: 1000;
    transform: translateX(-100%);
    width: var(--dynamic-sidebar-width, 280px) !important; // Use dynamic width even on mobile
    
    &.visible {
      transform: translateX(0);
    }
    
    // Hide toggle button on mobile
    .sidebar-toggle {
      display: none;
    }

    // RTL mobile positioning
    [dir="rtl"] & {
      left: auto;
      right: 0;
      transform: translateX(100%);

      &.visible {
        transform: translateX(0);
      }
    }
  }
}

// RTL Support - Move sidebar to right side
:root[dir="rtl"] .sidebar {
  box-shadow: -2px 0 8px var(--sidebar-shadow) !important; // Flip shadow direction
}

// Sidebar Header - Enhanced RTL Support
.sidebar-header {
  display: flex;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--sidebar-border);
  min-height: 64px;

  .company-logo {
    width: 32px;
    height: 32px;
    border-radius: 6px;
    object-fit: cover;
    flex-shrink: 0;
    transition: all 0.3s ease;
  }

  .company-logo-name {
    width: 145px;
    padding-top: 15px;
    padding-inline-start: 10px; // Use logical property for RTL support
    transition: all 0.3s ease;
  }

  .company-name {
    margin-inline-start: 12px; // Use logical property for RTL support
    font-weight: var(--menu-weight-semibold);
    font-size: var(--menu-text-large);
    color: var(--sidebar-text);
    transition: all 0.3s ease;
    white-space: nowrap;
    overflow: hidden;
  }

  .theme-toggle {
    margin-inline-start: auto; // Use logical property for RTL support
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: var(--sidebar-text);
    transition: all 0.2s ease;

    &:hover {
      background: var(--sidebar-hover);
    }

    .theme-icon {
      width: var(--sidebar-menu-icon-size);
      height: var(--sidebar-menu-icon-size);
    }
  }

  // Collapsed state - Enhanced RTL support
  .sidebar.collapsed & {
    justify-content: center;
    
    .company-logo {
      width: 28px;
      height: 28px;
    }

    .company-logo-name {
      width: 28px; // Match collapsed logo size
      padding-inline-start: 0; // Remove padding in collapsed state
      padding-top: 0; // Reset top padding
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
}

// RTL-specific header adjustments
[dir="rtl"] .sidebar-header {
  // Ensure proper RTL layout
  direction: rtl;

  .company-logo-name {
    // RTL-specific adjustments for logo name
    text-align: right;
  }

  // Collapsed state RTL adjustments
  .sidebar.collapsed & {
    .company-logo,
    .company-logo-name {
      // Ensure centered positioning in RTL collapsed state
      margin: 0 auto;
    }
  }
}

// Sidebar Content Areas - ChatGPT style compact
.sidebar-top {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 4px 0;
}

.sidebar-bottom {
  padding: 4px 0;
  margin-top: auto;
}

// Separator line between main menu and bottom section
.sidebar-separator {
  height: 1px;
  background: var(--sidebar-border);
  margin: 4px 12px 8px 12px;
}

.bottom-menu-items {
  margin-bottom: 4px;
}

// Toggle Button - Default to dark theme
.sidebar-toggle {
  position: absolute;
  top: 80px; // Position below header (60px + 20px)
  right: -12px;
  width: 28px;
  height: 28px;
  background: #2d2d2d;
  border: 1px solid #4a4a4a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 1001; // Above header (999) but below mobile overlay
  color: #ececec;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  outline: none;

  &:hover {
    background: #3a3a3a;
    transform: scale(1.1);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
    color: #ffffff;
    border-color: #5a5a5a;
  }

  &:focus {
    outline: none;
    background: #4a4a4a;
    border-color: #6a6a6a;
    color: #ffffff;
    box-shadow: 0 0 0 3px rgba(74, 74, 74, 0.3);
  }

  &:active {
    background: #1a1a1a;
    transform: scale(0.95);
    color: #cccccc;
  }

  .toggle-icon {
    width: var(--menu-icon-mini);
    height: var(--menu-icon-mini);
    transition: all 0.3s ease;
    stroke-width: 2.5;
  }

  .sidebar.collapsed & .toggle-icon {
    transform: rotate(180deg);
  }
}

// RTL Toggle Button positioning
:root[dir="rtl"] .sidebar-toggle {
  right: auto;
  left: -12px;
  
  .toggle-icon {
    transform: rotate(180deg);
  }
  
  .sidebar.collapsed & .toggle-icon {
    transform: rotate(0deg);
  }
}

// Light theme toggle button
:root[data-theme="light"] .sidebar-toggle {
  background: #ffffff;
  color: #374151;
  border-color: #64748b;

  &:hover {
    background: #f8fafc;
    color: #1f2937;
    border-color: #475569;
  }

  &:focus {
    background: #e2e8f0;
    border-color: #475569;
    color: #1f2937;
    box-shadow: 0 0 0 3px rgba(100, 116, 139, 0.2);
  }

  &:active {
    background: #cbd5e1;
    color: #0f172a;
  }
}

.sidebar-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  
  @media (min-width: 600px) {
    display: none;
  }
}
</style>
