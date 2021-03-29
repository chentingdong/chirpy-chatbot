<template>
    <div class="toggle" :message="message">
        <div v-b-toggle.collapse1 variant="primary" class="header">
            DEBUG
        </div>
        <b-collapse id="collapse1" class="mt-2">
            <pre>{{ message.message }}</pre>
        </b-collapse>
    </div>
</template>

<script>
export default {
  props: {
    message: {
      type: Object,
      required: true,
      default: ''
    }
  }
}
</script>

<style scoped>
</style>
