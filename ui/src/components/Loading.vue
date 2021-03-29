<template>
  <div :message="message" :loadingImage="loadingImage" class="loading">
    <img :src="loadingImage"/>
    <span>{{ message }}</span>
  </div>
</template>

<script>
export default {
  name: 'loading',
  props: {
    message: String,
    loadingImage: {
      default: require('@/assets/loading-dots.gif')
    }
  }
}
</script>

<style lang="sass">
.loading
  z-index: 10;
  background: transparent;
  img
    height: 41px;
    width: auto;
</style>
