<template>
  <div :data_json="data_json" class="image-slides">
    <carousel v-if="enabled" :perPageCustom="[[320, 1], [768, 3], [1024, 4]]">
      <slide v-for="(slide, index) in data_json" :key="index" class="slide">
        <div class="inner" v-on:click="$emit('clickToMessage', slide.title)">
          <img class="thumbnail" v-if="slide.image_url" :src="slide.image_url" alt="img blocked."/>
          <div class="text">
            <h1>{{ slide.title | truncate(50, '...') }}</h1>
            <div>{{ slide.description | truncate(200, ' ...') }}</div>
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
  min-height: 150px;
  text-align: left;
  box-sizing: border-box;
  .inner
    display: block;
    position: relative;
    min-height: 180px;
    overflow: hidden;
    cursor: pointer;
    background: #fff;
    color: #333;
    width: 100%;
    border-radius: 5px;
    padding: 20px;
    border: 1px solid $color-g6;
    border-left: 5px solid #7fe3b6;
    box-shadow: 1px 1px 10px 0px $color-g6;

    &:hover
      text-decoration: none !important;

    .text
      display: none;
      position: absolute;
      z-index: 1;
      h1
        font-size: 1em;
        font-weight: 700;
      .description
        font-size: 1em;

    .thumbnail
      position: absolute;
      top: 0;
      left: 0;
      z-index: 0;
      display: block;
      width: 3rem;
      height: 100;
      border-radius: $border-radius;

</style>
