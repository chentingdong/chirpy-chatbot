<template>
  <div :data_json="data_json" class="text-buttons" v-if="showButtons">
    <ul>
      <li v-for="(button, index) in data_json" :key="index" :style="{display: display}">
        <div class="btn btn-secondary btn-sm click-effect" v-on:click="clickTextButton(button)">{{ button }}</div>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  props: {
    data_json: {
      type: Array,
      required: true
    }
  },
  data: function () {
    return {
      showButtons: true
    }
  },
  computed: {
    display () {
      return this.data_json.length > 3 ? 'block' : 'inline-block'
    }
  },
  methods: {
    clickTextButton: function (button) {
      this.showButtons = false
      this.$emit('clickToMessage', button)
    }
  }
}
</script>

<style lang="sass">
.text-buttons
  li
    margin: 0.5em 0.5em 0 0;
    .btn
      white-space: normal;
      text-align: left;
      cursor: pointer;

</style>
