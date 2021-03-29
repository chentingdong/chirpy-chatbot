<template>
  <div class="show-codes">
    <h1>{{options.title}}</h1>
    <codemirror v-bind:value="codes" readOnly="true"></codemirror>
    <v-btn @click="handleProceed">ok</v-btn>
  </div>
</template>

<script>
import VuejsDialogMixin from 'vuejs-dialog/dist/vuejs-dialog-mixin.min.js'

export default {
  name: 'ShowCodes',
  mixins: [VuejsDialogMixin],
  props: {
    data: {}
  },
  computed: {
    codes () {
      var codes = this.data
      if (this.options.lang === 'json') {
        codes = JSON.stringify(this.options.data, null, 4)
      }
      return codes
    }
  },
  methods: {
    // included in DialogMixin
    handleProceed (platform) {
      this.proceed(platform)
    }
  }
}
</script>
<style lang="sass" scoped>
@import "@/assets/variables.scss";

.CodeMirror
  height: calc(100% - 150px);

</style>
