<template>
  <div id="app" ref="app" :class="viewport">
    <div data-app>
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: 'app',
  components: {},
  data: function () {
    return {
      'viewport': this.$currentViewport.label
    }
  },
  head: {
    title: {
      inner: 'Astound Answers'
    },
    meta: [
      { name: 'viewport', content: 'width=device-width height=device-height initial-scale=1 user-scalable=no' }
    ]
  },
  mounted: function () {
    // fix mobile device height to exclude title bar
    const vh = window.innerHeight * 0.01
    document.documentElement.style.setProperty('--vh', `${vh}px`)
  }
}
</script>

<style lang="sass">
@import "@/assets/variables.scss";
</style>
