import { useEffect, useState } from "react";
import { getCourses } from "../api/courses";

function Home() {
    const [courses, setCourses] = useState([]);

    useEffect(() => {
        getCourses()
            .then((data) => {
            console.log("DATA:", data);
            setCourses(data.courses);
            })
            .catch(console.error);
        }, []);

    return (
        <div>
            <h2>Courses</h2>
            <ul>
                {courses.map((course) => (
                    <li key={course.id}>{course.name}</li>
                ))}
            </ul>
        </div>
    );
}

export default Home;