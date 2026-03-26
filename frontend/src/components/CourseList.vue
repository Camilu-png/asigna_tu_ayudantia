<script setup>
import { onMounted, ref } from "vue";
import apiClient from "../api/courses";

const courses = ref([]);

onMounted(async () => {
  try {
    const response = await getCourses();
    courses.value = response.courses;
  } catch (error) {
    console.error("Error fetching courses:", error);
  }
});
</script>

<template>
  <div>
    <h1>Course List</h1>
    <ul>
      <li v-for="course in courses" :key="course.id">
        {{ course.name }}
      </li>
    </ul>
  </div>
</template>
