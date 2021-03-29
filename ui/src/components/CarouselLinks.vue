<template>
  <div :data_json="data_json" class="carousel-links">
    <carousel :perPageCustom="[[320, 1], [600, 2], [1024, 3], [2048, 6]]">
      <slide v-for="(slide, index) in data_json" :key="index" class="slide">
        <div class="inner">
          <a v-bind:href="slide.url" target="_blank">{{ slide.title }}</a>
          <p>{{ slide.description | truncate(100, ' ...') }}</p>
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
      type: Array,
      required: true
    }
  }
}
</script>

<style scoped lang="sass">
@import "@/assets/variables.scss";

.carousel-links
  padding: 10px 20px 20px 0;

.VueCarousel
  font-size: 0.8em;

.slide
  position: relative;
  padding: 10px;

.inner
  text-align: left;
  box-sizing: border-box;
  border-radius: 5px;
  padding: 20px;
  border: 1px solid $color-g6;
  border-left: 6px solid #7fe3b6;
  box-shadow: 1px 1px 10px 0px $color-g6;
  a:hover
    text-decoration: none !important;
  p
    margin-top: 10px;
</style>
