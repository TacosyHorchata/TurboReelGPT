# MoviePy Video Engine  

TurboReel initially relied on **moviepy** as its video engine. However, we are transitioning to **Revideo**, which is built on top of the powerful **MotionCanvas** framework. This shift is driven by the following reasons:

- **MoviePy** is no longer actively maintained.
- **Revideo** provides advanced video manipulation capabilities and supports a more modern development experience.

## Using Moviepy  

If you still prefer to use **MoviePy**, we've included examples to run deprecated workflows showcasing how **MediaChain** can be utilized with it.  

### Pros of MoviePy:
- Simple and intuitive for basic video manipulations.
- Easy to set up and run.

### Cons of MoviePy:
- Limited flexibility (e.g., restricted animation capabilities).
- No active maintenance.
- No live preview, requires rendering to view results.

While MoviePy may still be a great tool for some users, we encourage the community to consider adopting and maintaining the library if they find value in it.  

---

## Why Revideo?  

**Revideo** offers enhanced control and features for developers, making it a robust choice for modern video workflows. 

### Pros of Revideo:
- Advanced animation and manipulation options.
- Support for live previews during development.
- A growing ecosystem built on **MotionCanvas**.

### Cons of Revideo:
- Written in Typescript(since MediaChain is written in Python).
- Harder to learn for new developers.
- Rendering is just available in the browser, CLI or in a server environment.

While we continue to explore the best video engines for **TurboReel**, **MediaChain** remains compatible with various engines, ensuring flexibility for users. For projects requiring more precise control over video manipulations and faster development cycles, we highly recommend using **Revideo**.

---

Let us know how you’re using **MediaChain** and share your experiences with either **MoviePy** or **Revideo**, we’re excited to hear from you!
