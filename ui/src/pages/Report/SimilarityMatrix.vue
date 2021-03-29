<template>
  <div class="similarity-matrix">
    <loading v-if="loading"></loading>
    <svg :class="'matrix-' + plotIndex" class="matrix"></svg>
    <svg :class="'color-scale-' + plotIndex" class="color-scale"></svg>
    <slot class="cell-info"></slot>
  </div>
</template>

<script lang='js'>
import * as d3 from 'd3'
import Loading from '@/components/Loading'

export default {
  name: 'a-similarity-matrix',
  components: {
    'loading': Loading
  },
  props: {
    matrix: {
      type: Array
    },
    cellSpacing: {
      type: Number,
      default: 1
    },
    showLabel: {
      type: Boolean,
      default: false
    },
    plotIndex: {
      type: Number
    },
    color: {
      type: String,
      default: 'neva'
    }
  },
  data () {
    return {
      title: 'Similarity Matrix',
      loading: false,
      width: 0,
      tickSize: 5,
      ticks: 10,
      valueRange: [-0.1, 1.1],
      colorScales: {
        'neva': [d3.rgb('#3E9998'), d3.rgb('#FF7874')],
        'astound': [d3.rgb('#3E9998'), d3.rgb('#D2FDD2')],
        'crazy green': [d3.rgb('#007AFF'), d3.rgb('#FFF500')],
        'neon': [d3.rgb('#ff58a8'), d3.rgb('#fff200')]
      },
      blankColor: '#FFFFFF'
    }
  },
  computed: {
  },
  watch: {
    matrix: function () {
      const vm = this
      const wrapper = d3.select('.similarity-matrix')
      vm.matrixSize = vm.matrix.length
      vm.width = wrapper.style('width').slice(0, -2)
      vm.ticks = Math.max(Math.floor(vm.width / 70), 5)
      vm.plotSimilarityMatrix()
      vm.plotColorScale()
    }
  },
  methods: {
    plotSimilarityMatrix: function () {
      const vm = this
      vm.cellSize = vm.width / vm.matrixSize - vm.cellSpacing

      var matrixSvg = d3.select('.matrix-' + vm.plotIndex)
      matrixSvg.selectAll('.row').remove()

      matrixSvg
        .attr('height', vm.width)
        .attr('width', vm.width)

      var pos = function (d, i) {
        return i * (vm.cellSize + vm.cellSpacing)
      }

      var row = matrixSvg.selectAll('.row')
        .data(vm.matrix)
        .enter()
        .append('g')
        .attr('class', 'row')
        .attr('transform', (d, i) => {
          return 'translate(0, ' + pos(d, i) + ')'
        })

      var cell = row.selectAll('.cell')
        .data((d) => { return d })
        .enter()
        .append('rect')
        .attr('class', 'cell')

      cell
        .attr('x', (d, i) => pos(d, i))
        .attr('width', vm.cellSize)
        .attr('height', vm.cellSize)
        .attr('fill', (d, i) => {
          return vm.colorScale(d.similarity)
        })
        .attr('cell_y', (d, i) => {
          return d.cell_y
        })
        .attr('cell_x', (d, i) => {
          return d.cell_x
        })
        .on('mouseover', (d) => {
          vm.$emit('showCellInfo', d)
        })
        .on('click', (d) => {
          vm.$emit('showCellDetails', d)
        })
    },

    plotColorScale: function () {
      const vm = this
      var colorSvg = d3.select('.color-scale-' + vm.plotIndex)

      const svgGradient = colorSvg
        .append('linearGradient')
        .attr('id', 'gradient')

      svgGradient
        .append('stop')
        .attr('stop-color', vm.colorScale(0))
        .attr('offset', '0')

      svgGradient
        .append('stop')
        .attr('stop-color', vm.colorScale(1))
        .attr('offset', '1')

      colorSvg
        .append('rect')
        .attr('x', 0)
        .attr('y', 0)
        .attr('width', '100%')
        .attr('height', '100%')
        .attr('fill', 'url(#gradient)')

      const legendScale = d3
        .scaleLinear()
        .domain(vm.valueRange)
        .range([0, vm.width])

      var legendAxis = d3
        .axisBottom(legendScale)
        .tickSize(5)
        .ticks(vm.ticks)

      colorSvg.append('g')
        .attr('class', 'legend axis')
        .call(legendAxis)
    },

    colorScale: function (sim) {
      const vm = this
      var colorFunc = d3.scaleLinear()
        .domain(vm.valueRange)
        .interpolate(d3.interpolateHslLong)
        .range(vm.colorScales[vm.color])

      var color = vm.blankColor
      if (sim > vm.valueRange[0] && sim < vm.valueRange[1]) {
        color = colorFunc(sim)
      }

      return color
    }
  }
}
</script>

<style lang='sass'>
@import '@/assets/variables.scss'
@import 'node_modules/bootstrap/scss/bootstrap'

.matrix
  border: 1px dotted $color-border
  width: 100%
  height: 100%
  .cells
    fill: #aaa
  .label
    text-anchor: start
    font: 24px sans-serif
  .cell
    &.active
      stroke: $color-c8;
.color-scale
  margin-top: 10px
  width: 100%
  height: 30px
</style>
