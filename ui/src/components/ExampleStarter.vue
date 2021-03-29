<template>
  <div :data="data_json" class="example-starter">
    {{data_json}}
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
  data () {
    return {
      title: 'Example Starter'
    }
  }
}
</script>

<style lang="sass">
@import '@/assets/variables.scss';
</style>
