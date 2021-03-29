<template>
  <div :data="data_json" class="link-buttons">
    <ul>
      <li v-for="(item, index) in data_json" :key="'less-'+index">
        <a v-if="index<3" v-bind:href="item.url" target="_blank" >{{ item.title }}</a>
      </li>
      <li v-for="(item, index) in data_json" :key="'more-'+index">
        <a v-if="index >= 3 && showAll" v-bind:href="item.url" target="_blank">{{ item.title }}</a>
      </li>
    </ul>
    <a href="" v-if="data_json.length > 3 && ! showAll" v-on:click="showAllLinks">Show more</a>
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
      showAll: false
    }
  },
  methods: {
    showAllLinks: function (e) {
      e.preventDefault()
      this.showAll = true
    }
  }
}
</script>

<style lang="sass">
@import '@/assets/variables.scss';

.link-buttons
  li
    display: block;
    font-size: 0.9em;
    a:hover
      color: $color-c6;
      text-decoration: none;
</style>
