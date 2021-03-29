<template>
  <div :data_json="data_json" class="image-slides">
    <carousel v-if="enabled" :perPageCustom="[[320, 1], [480, 2], [1024, 3], [2048, 4]]">
      <slide v-for="(slide, index) in data_json" :key="index" class="slide">
        <div class="inner" v-on:click="$emit('clickToMessage', slide.title)">
          <figure>
            <img v-if="slide.image_url" :src="slide.image_url" alt="img blocked."/>
          </figure>
          <div class="text">
            <h1>{{ slide.title }}</h1>
            <div>{{ slide.description | truncate(100, ' ...') }}</div>
          </div>
        </div>
      </slide>
    </carousel>
  </div>
</template>

<script>
import { Carousel, Slide } from 'vue-carousel'
export default {
  components: {
    Carousel,
    Slide
  },
  props: {
    data_json: {
      type: Array
    }
  },
  computed: {
    enabled: function () {
      console.log(this.data_json)
      return typeof this.data_json === 'undefined' ? 0 : this.data_json.length
    }
  }
}
</script>

<style scoped lang="sass">
@import "@/assets/variables.scss";

.VueCarousel
  font-size: 0.8em;

.slide
  position: relative;
  padding: 10px;
  color: rgba(255, 255, 255, 0.9);
  text-align: left;
  box-sizing: border-box;
  .inner
    display: block;
    cursor: pointer;
    background: #fff;
    color: #333;
    width: 100%;
    border-radius: 5px;
    padding: 10px;
    border: 1px solid $color-g6;
    border-left: 5px solid #7fe3b6;
    box-shadow: 1px 1px 10px 0px $color-g6;

    &:hover
      text-decoration: none !important;

  .text
    font-size: 0.7em;
    leight-height: 1em;
    h1
      font-size: 1em;
      font-weight: 700;
      margin: 0;
  figure
    margin: 10px 15px 10px 0;
    height: 100px;
    width: 100px;
    overflow: hidden;
    float: left;
    position: relative;
    border-radius: $border-radius;
    border: 1px solid $color-g4;
    img
      display: block;
      min-width: 100%;
      max-width: 200%;
      min-height: 100%;
      margin: auto;
      position: absolute;
      top: -100%;
      right: -100%;
      bottom: -100%;
      left: -100%;

</style>
