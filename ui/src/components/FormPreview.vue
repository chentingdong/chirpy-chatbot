<template>
  <div :data="data_json" class="form-preview">
    <ul v-for="(answer, question) in data_json" :key="'form'-index" class="form-entry">
      <li>
        <label>{{question}}</label>
        <div>{{answer}}</div>
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
  data () {
    return {
      title: 'Form preview'
    }
  }
}
</script>

<style lang="sass" scoped>
@import '@/assets/variables.scss';
.form-preview
  padding: 1em 2em;
  border-radius: $border-radius;
  li
    list-style: disc;

</style>
