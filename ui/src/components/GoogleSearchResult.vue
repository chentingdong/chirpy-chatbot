<template>
  <div :data_json="data_json" class="google-search-result">
    <div v-for="(result, index) in data_json" :key="index">
      <a v-bind:href="result.link" target="_blank">
        <h4>{{result.name}}</h4>
      </a>
      <p>{{result.description}}</p>
    </div>
  </div>
</template>

<script>
export default {
  components: {},
  props: {
    data_json: {
      type: Array,
      required: true
    }
  }
}
</script>

<style lang="sass">
.google-search-result
  font-size: 0.8em;
  font-style: italic;
</style>
