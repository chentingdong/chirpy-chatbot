<template>
  <div v-if="hasData" :data_json="data_json" class="data-slides" v-cloak>
    <carousel class="row-eq-height" v-if="useCarousel" :perPageCustom="[[320, 1], [600, 2], [1024, 3], [2048, 6]]">
      <slide v-for="(row, index) in data_json" :key="index" class="slide ">
        <a v-if="row.external_url" v-bind:href="row.external_url" target="_blank">
          <div class="inner">
            <div v-for="(value, key) in row" :key="key">
              <label v-if="key !== 'external_url'"> {{key.replace('_', ' ')}}:&nbsp;</label>
              <span v-if="key !== 'external_url'">{{value | truncate(120, '...')}}</span>
            </div>
          </div>
        </a>
        <div v-else-if="row.message">
          <div class="inner btn btn-light btn-sm click-effect" v-on:click="$emit('clickToMessage', row.message)">
            <div v-for="(value, key) in row" :key="key">
              <label v-if="key !== 'message'"> {{key.replace('_', ' ')}}:&nbsp;</label>
              <span v-if="key !== 'message'">{{value}}</span>
            </div>
          </div>
        </div>
        <div v-else class="inner">
          <div v-for="(value, key) in row" :key="key">
            <label> {{key.replace('_', ' ')}}:&nbsp;</label><span>{{value}}</span>
          </div>
        </div>
      </slide>
    </carousel>
    <div v-else>
      <div class="slide">
        <a v-if="data_json[0].external_url" v-bind:href="data_json[0].external_url" target="_blank">
          <div class="inner">
            <div v-for="(value, key) in data_json[0]" :key="key">
              <label v-if="key !== 'external_url'"> {{key.replace('_', ' ')}}:&nbsp;</label>
              <span v-if="key !== 'external_url'">{{value | truncate(120, '...')}}</span>
            </div>
          </div>
        </a>
        <div v-else-if="data_json[0].message">
          <div class="inner btn btn-light btn-sm click-effect" v-on:click="$emit('clickToMessage', data_json[0].message)">
            <div v-for="(value, key) in data_json[0]" :key="key">
              <label v-if="key !== 'message'"> {{key.replace('_', ' ')}}:&nbsp;</label><span>{{value}}</span>
            </div>
          </div>
        </div>
        <div v-else class="inner">
          <div v-for="(value, key) in data_json[0]" :key="key">
            <label> {{key.replace('_', ' ')}}:&nbsp;</label><span>{{value}}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Carousel, Slide } from 'vue-carousel'

export default {
  name: 'data-slides',
  components: {
    Carousel,
    Slide
  },
  props: {
    data_json: {}
  },
  computed: {
    hasData: function () {
      return Array.isArray(this.data_json) && this.data_json.length > 0
    },
    useCarousel: function () {
      return this.data_json.length > 1
    }
  },
  methods: {}
}
</script>

<style lang="sass">
@import '@/assets/variables.scss';

.VueCarousel
  font-size: 0.8em;
  margin: 0 1em 0 -1em;
  .VueCarousel-navigation button
    padding: 0.2em;
    top: calc(50% - 0.5em) !important;

.slide
  position: relative;
  padding: 10px;
  text-align: left;
  box-sizing: border-box;

  .inner
    height: 100%;
    display: block;
    cursor: pointer;
    width: 100%;
    border-radius: 5px;
    padding: 20px;
    border: 1px solid;
    border-left: 5px solid #7fe3b6;
    box-shadow: 1px 1px 3px 1px $color-g6;
    line-height: 0.8em;
    >div
      line-height: 1em;
      padding: 5px 0;
      label
        display: inline;
        font-weight: 700;
        text-transform: capitalize;
      span
        font-size: 0.9em;

  a:hover
    text-decoration: none;
    color: $color-c6;

</style>
