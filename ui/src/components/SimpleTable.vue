<template>
  <div :data_json="data_json" class="simple-table">
    <b-table :items="data_json"></b-table>
  </div>
</template>

<script>

export default {
  props: {
    data_json: {
      type: Array,
      required: true
    }
  }
}
</script>

<style scoped>
.simple-table table {
  font-size: 0.7em;
  margin: 10px 0;
}
</style>
